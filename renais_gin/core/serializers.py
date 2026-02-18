"""
Serializers for Renais Gin API.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.conf import settings
from .models import (
    User, UserProfile, Bottle, KarmaPledge, PledgeValidation,
    Rebate, CommunityCircle, UserPDFDocument, GeneratedReport
)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'engagement_score', 'preferred_causes', 'impact_history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['engagement_score', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'last_login', 'is_active', 'karma_score',
            'country', 'profile'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'is_active', 'profile'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'country'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'country': {'required': False},
        }

    def validate_username(self, value):
        """Validate username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError('Must include username and password')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'country'
        ]
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        """Validate email is unique excluding current user"""
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value


class BottleSerializer(serializers.ModelSerializer):
    registered_to_username = serializers.CharField(source='registered_to.username', read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    can_make_pledge = serializers.BooleanField(read_only=True)
    has_pledge = serializers.BooleanField(read_only=True)

    class Meta:
        model = Bottle
        fields = [
            'id', 'bottle_id', 'batch_id', 'production_date',
            'terroir_region', 'terroir_vintage', 'registered',
            'registered_to', 'registered_to_username', 'registration_date',
            'qr_code', 'qr_code_url', 'status', 'can_make_pledge', 'has_pledge',
            'created_at'
        ]
        read_only_fields = [
            'id', 'registration_date', 'qr_code', 'status', 'created_at',
            'can_make_pledge', 'has_pledge'
        ]

    def get_qr_code_url(self, obj):
        if obj.qr_code:
            return obj.qr_code.url
        return None


class BottleRegistrationSerializer(serializers.Serializer):
    bottle_id = serializers.CharField(max_length=100)

    def validate_bottle_id(self, value):
        """Validate bottle exists and can be registered"""
        from .models import Bottle
        try:
            bottle = Bottle.objects.get(bottle_id=value)
            if bottle.registered:
                raise serializers.ValidationError("This bottle has already been registered.")
        except Bottle.DoesNotExist:
            raise serializers.ValidationError("Bottle ID not found in our system.")
        return value


class KarmaPledgeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    bottle_id_display = serializers.CharField(source='bottle.bottle_id', read_only=True)
    approval_count = serializers.IntegerField(read_only=True)
    rejection_count = serializers.IntegerField(read_only=True)
    total_validations = serializers.IntegerField(read_only=True)
    approval_percentage = serializers.SerializerMethodField()

    class Meta:
        model = KarmaPledge
        fields = [
            'id', 'submission_id', 'user', 'user_username', 'user_email', 'bottle',
            'bottle_id_display', 'pledge_text', 'impact_plan', 'impact_type',
            'status', 'sentiment_score', 'ai_validation_data',
            'approval_count', 'rejection_count', 'total_validations', 'approval_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'submission_id', 'user', 'sentiment_score',
            'ai_validation_data', 'created_at', 'updated_at',
            'approval_count', 'rejection_count', 'total_validations', 'approval_percentage'
        ]

    def get_approval_percentage(self, obj):
        """Calculate approval percentage"""
        total = obj.total_validations
        if total == 0:
            return 0
        return (obj.approval_count / total) * 100

    def validate_pledge_text(self, value):
        """Validate pledge text length"""
        if len(value) < 20:
            raise serializers.ValidationError("Pledge must be at least 20 characters long.")
        if len(value) > 500:
            raise serializers.ValidationError("Pledge must be less than 500 characters.")
        return value

    def validate_impact_plan(self, value):
        """Validate impact plan length"""
        if len(value) < 20:
            raise serializers.ValidationError("Impact plan must be at least 20 characters long.")
        if len(value) > 500:
            raise serializers.ValidationError("Impact plan must be less than 500 characters.")
        return value


class PledgeValidationSerializer(serializers.ModelSerializer):
    validator_username = serializers.CharField(source='validator.username', read_only=True)
    validator_email = serializers.CharField(source='validator.email', read_only=True)
    pledge_submission_id = serializers.CharField(source='pledge.submission_id', read_only=True)
    pledge_text_preview = serializers.CharField(source='pledge.pledge_text', read_only=True)
    pledge_user_username = serializers.CharField(source='pledge.user.username', read_only=True)

    class Meta:
        model = PledgeValidation
        fields = [
            'id', 'pledge', 'pledge_submission_id', 'pledge_text_preview',
            'pledge_user_username', 'validator', 'validator_username', 'validator_email',
            'approved', 'comments', 'validator_ip', 'validator_user_agent', 'created_at'
        ]
        read_only_fields = [
            'id', 'validator', 'validator_ip', 'validator_user_agent', 'created_at'
        ]

    def validate(self, attrs):
        """Ensure user cannot validate their own pledge"""
        pledge = attrs.get('pledge')
        request = self.context.get('request')

        if request and pledge.user == request.user:
            raise serializers.ValidationError("You cannot validate your own pledge.")

        return attrs


class RebateSerializer(serializers.ModelSerializer):
    pledge_submission_id = serializers.CharField(source='pledge.submission_id', read_only=True)
    user_username = serializers.CharField(source='pledge.user.username', read_only=True)
    user_email = serializers.CharField(source='pledge.user.email', read_only=True)
    pledge_text_preview = serializers.CharField(source='pledge.pledge_text', read_only=True)

    class Meta:
        model = Rebate
        fields = [
            'id', 'pledge', 'pledge_submission_id', 'user_username', 'user_email',
            'pledge_text_preview', 'amount', 'status', 'transaction_id', 'processed_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'amount', 'transaction_id', 'processed_date',
            'created_at', 'updated_at'
        ]


class CommunityCircleSerializer(serializers.ModelSerializer):
    leader_username = serializers.CharField(source='leader.username', read_only=True)
    leader_email = serializers.CharField(source='leader.email', read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    total_members = serializers.IntegerField(read_only=True)
    members_usernames = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    is_leader = serializers.SerializerMethodField()

    class Meta:
        model = CommunityCircle
        fields = [
            'id', 'name', 'leader', 'leader_username', 'leader_email', 'location',
            'description', 'focus_areas', 'is_active', 'member_count', 'total_members',
            'members_usernames', 'is_member', 'is_leader', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'leader', 'created_at', 'updated_at']

    def get_members_usernames(self, obj):
        return list(obj.members.values_list('username', flat=True))

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists() or obj.leader == request.user
        return False

    def get_is_leader(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.leader == request.user
        return False

    def validate_name(self, value):
        """Validate circle name is unique"""
        if CommunityCircle.objects.filter(name=value).exists():
            raise serializers.ValidationError("A community circle with this name already exists.")
        return value


class CommunityCircleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityCircle
        fields = ['name', 'location', 'description', 'focus_areas']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['leader'] = request.user
        return super().create(validated_data)


class UserPDFDocumentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    file_size = serializers.FloatField(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UserPDFDocument
        fields = [
            'id', 'user', 'user_username', 'title', 'description',
            'pdf_file', 'file_url', 'file_size', 'uploaded_at', 'is_verified'
        ]
        read_only_fields = ['id', 'user', 'uploaded_at', 'file_size', 'file_url']

    def get_file_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None

    def validate_pdf_file(self, value):
        """Validate PDF file"""
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size must be under 10MB.")
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        return value


class GeneratedReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'report_type', 'report_type_display', 'title', 'description',
            'pdf_file', 'file_url', 'file_size', 'generated_at', 'related_pledge'
        ]
        read_only_fields = ['id', 'generated_at', 'file_url', 'file_size']

    def get_file_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None

    def get_file_size(self, obj):
        if obj.pdf_file:
            return round(obj.pdf_file.size / (1024 * 1024), 2)
        return 0


class UserMetricsSerializer(serializers.Serializer):
    total_pledges = serializers.IntegerField()
    approved_pledges = serializers.IntegerField()
    pending_pledges = serializers.IntegerField()
    total_bottles = serializers.IntegerField()
    validations_given = serializers.IntegerField()
    engagement_score = serializers.IntegerField()
    karma_score = serializers.FloatField()
    total_impact = serializers.FloatField()
    preferred_causes = serializers.ListField(child=serializers.CharField())
    member_since = serializers.CharField()


class MovementMetricsSerializer(serializers.Serializer):
    total_community = serializers.IntegerField()
    total_bottles = serializers.IntegerField()
    total_pledges = serializers.IntegerField()
    approved_pledges = serializers.IntegerField()
    total_rebates = serializers.IntegerField()
    total_impact = serializers.FloatField()
    active_circles = serializers.IntegerField()
    total_circle_members = serializers.IntegerField()
    impact_by_category = serializers.DictField(child=serializers.IntegerField())


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(min_length=8, style={'input_type': 'password'})

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(min_length=8, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs


class ImpactStorySerializer(serializers.Serializer):
    pledge_id = serializers.UUIDField()
    user_username = serializers.CharField()
    pledge_text = serializers.CharField()
    impact_plan = serializers.CharField()
    impact_type = serializers.CharField()
    created_at = serializers.DateTimeField()
    total_impact = serializers.FloatField()


class LeaderboardEntrySerializer(serializers.Serializer):
    username = serializers.CharField()
    karma_score = serializers.FloatField()
    engagement_score = serializers.IntegerField()
    total_pledges = serializers.IntegerField()
    approved_pledges = serializers.IntegerField()
    total_impact = serializers.FloatField()
    country = serializers.CharField(allow_blank=True)


class LeaderboardSerializer(serializers.Serializer):
    top_users = LeaderboardEntrySerializer(many=True)
    top_circles = CommunityCircleSerializer(many=True)


class ValidationOpportunitySerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    bottle_id_display = serializers.CharField(source='bottle.bottle_id', read_only=True)
    approval_count = serializers.IntegerField(read_only=True)
    rejection_count = serializers.IntegerField(read_only=True)
    total_validations = serializers.IntegerField(read_only=True)
    has_validated = serializers.SerializerMethodField()

    class Meta:
        model = KarmaPledge
        fields = [
            'id', 'submission_id', 'user', 'user_username', 'bottle',
            'bottle_id_display', 'pledge_text', 'impact_plan', 'impact_type',
            'status', 'approval_count', 'rejection_count', 'total_validations',
            'has_validated', 'created_at'
        ]
        read_only_fields = fields

    def get_has_validated(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.validations.filter(validator=request.user).exists()
        return False
