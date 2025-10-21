# community/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import CommunityCircle, CommunityStory
from .serializers import CommunityCircleSerializer, CommunityStorySerializer

class CommunityCircleListCreateView(generics.ListCreateAPIView):
    queryset = CommunityCircle.objects.filter(is_active=True)
    serializer_class = CommunityCircleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(leader=self.request.user)

class CommunityCircleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommunityCircle.objects.all()
    serializer_class = CommunityCircleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CommunityStoryListCreateView(generics.ListCreateAPIView):
    queryset = CommunityStory.objects.all()
    serializer_class = CommunityStorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommunityStoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommunityStory.objects.all()
    serializer_class = CommunityStorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
