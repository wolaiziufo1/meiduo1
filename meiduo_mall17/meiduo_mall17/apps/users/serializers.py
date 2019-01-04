import re

from rest_framework import serializers
from django_redis import get_redis_connection

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    allow = serializers.CharField(write_only=True)
    sms_code = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'allow', 'sms_code', 'mobile')

    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError("协议未同意")
        return value

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}', value):
            raise serializers.ValidationError("请输入正确的手机号")
        return value

    def validate(self, attrs):
        # 密码验证
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("密码不一致")

        # 短信验证
        # 1.连接redis
        conn = get_redis_connection('verify')
        # 2.获取验证码
        sms_data = conn.get('sms_%s' % attrs['mobile'])
        # 判断是否超过有效期
        if not sms_data:
            raise serializers.ValidationError("短信失效")
        sms_data = sms_data.decode()
        # 3.验证验证码
        if sms_data != attrs['sms_code']:
            raise serializers.ValidationError("请输入正确验证码")
        # 4.返回结果
        return attrs

    def create(self, validated_data):
        del validated_data['allow']
        del validated_data['password2']
        del validated_data['sms_code']

        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


