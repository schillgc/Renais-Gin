# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer,
    UserRegistrationSerializer, UserLoginSerializer
)


# Template views
def home_view(request):
    return render(request, 'home.html')


def about_view(request):
    return render(request, 'about.html')


def dashboard_view(request):
    return render(request, 'dashboard.html')


def bottles_view(request):
    return render(request, 'bottles.html')


def karma_view(request):
    return render(request, 'karma.html')


# API views (keep your existing API views)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Auto-login after registration
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return Response({'message': 'Logout successful'})


class UserStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile

        stats = {
            'karma_score': user.karma_score,
            'total_pledges': profile.total_pledges,
            'approved_pledges': profile.approved_pledges,
            'total_rebates': float(profile.total_rebates),
        }

        return Response(stats)
