from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from users.models import User
from .serializers import CreateUserSerializer


# Create your views here.


# 判断用户名是否存在
class UserNameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return Response({'count': count})


# 判断手机号是否存在
class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return Response({'count': count})


# 注册用户
class UserView(CreateAPIView):
    serializer_class = CreateUserSerializer
