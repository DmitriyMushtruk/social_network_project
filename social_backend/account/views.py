from django.shortcuts import render

from rest_framework import generics
from .models import User
from .serializers.user_serializer import UserSerializer
from django.http import HttpResponse

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

def hello(request):
    return HttpResponse("Hello World...")