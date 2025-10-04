from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from aaa.serializers.otp_verify import OTPVerifySerializer
from aaa.serializers.auth_signup import SignupSerializer
from aaa.utils.jwt_tokens import generate_jwt_response


class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            xponse = Response(generate_jwt_response(user, SignupSerializer), status=status.HTTP_200_OK)
            xponse.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],  # usually 'refresh_token'
                value=str(refresh),
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['AUTH_COOKIE_MAX_AGE'],
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
            )
            return xponse
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
