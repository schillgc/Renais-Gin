from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Bottle
from .serializers import BottleSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def register_bottle(request):
    if request.method == 'POST':
        bottle_id = request.POST.get('bottle_id')
        # ... process bottle registration ...
        # Redirect to bottle detail or pledge page
    return render(request, 'bottles/register_bottle.html')


class UserBottlesView(generics.ListAPIView):
    serializer_class = BottleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bottle.objects.filter(registered_to=self.request.user).select_related('batch')


class BottleRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Simplified implementation for now
        return Response({
            'message': 'Bottle registration endpoint - implementation pending'
        }, status=status.HTTP_200_OK)


class BottleDetailView(generics.RetrieveAPIView):
    serializer_class = BottleSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'bottle_id'
    lookup_url_kwarg = 'bottle_id'

    def get_queryset(self):
        return Bottle.objects.filter(registered_to=self.request.user).select_related('batch')
