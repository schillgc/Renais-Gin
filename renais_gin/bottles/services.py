# bottles/services.py
import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings
from .models import Bottle


class BottleQRService:
    @staticmethod
    def generate_qr_code(bottle: Bottle) -> str:
        """Generate QR code for a bottle and save to media storage"""
        bottle_data = {
            'bottle_id': bottle.bottle_id,
            'batch_id': bottle.batch.batch_id,
            'production_date': bottle.batch.production_date.isoformat(),
            'region': bottle.batch.region,
        }

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(bottle_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        # Save to ImageField
        filename = f"qr_{bottle.bottle_id}.png"
        bottle.qr_code.save(filename, File(buffer), save=True)

        return bottle.qr_code.url


class BottleRegistrationService:
    def __init__(self):
        self.qr_service = BottleQRService()

    def register_bottle(self, bottle_id: str, user) -> dict:
        """Register a bottle to a user"""
        try:
            bottle = Bottle.objects.get(bottle_id=bottle_id)

            if bottle.is_registered:
                return {
                    'success': False,
                    'error': 'Bottle already registered',
                    'bottle_id': bottle_id
                }

            # Generate QR code if not exists
            if not bottle.qr_code:
                self.qr_service.generate_qr_code(bottle)

            # Register bottle
            bottle.is_registered = True
            bottle.registered_to = user
            bottle.registration_date = timezone.now()
            bottle.save()

            return {
                'success': True,
                'bottle': bottle,
                'karma_access': True,
                'rebate_available': True
            }

        except Bottle.DoesNotExist:
            return {
                'success': False,
                'error': 'Bottle not found',
                'bottle_id': bottle_id
            }
