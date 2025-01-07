from django.shortcuts import render
from rest_framework import generics, pagination, viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from .models import Chat
from .paginations import CustomPagination
from .serializers import ChatSerializer

class ChatAPIView(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(owner=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()

class ChatDetailAPIView(generics.ListAPIView, generics.DestroyAPIView):
    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        try:
            chat = Chat.objects.get(owner=request.user)
            serializer = self.get_serializer(chat)
            return Response(serializer.data)
        except Chat.DoesNotExist:
            return Response({"detail": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise NotFound("Chat not found.")
        else:
            instance.delete()