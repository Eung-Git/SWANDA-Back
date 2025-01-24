from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken    
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import *

class SignupView(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        if TemporaryUser.objects.filter(email=email).exists() and TemporaryUser.objects.get(email=email).is_certified:
            serializer = SignupSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                return Response({"detail": "회원가입 성공"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "이메일 인증이 안 됨"}, status=status.HTTP_400_BAD_REQUEST)
    
class CheckNicknameView(APIView):
    def post(self, request):
        nickname = request.data.get('nickname')
        if User.objects.filter(nickname=nickname).exists():
            return Response({"detail": "이미 존재하는 nickname입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "사용 가능한 nickname입니다."}, status=status.HTTP_200_OK)

def send_verification_email(email):
    verification_code = str(random.randint(100000, 999999))
    
    subject = "SWANDA 이메일 인증 요청"
    message = f"SWANDA 비밀번호 변경 인증 메일입니다.\n\n인증번호: {verification_code}\n\n해당 인증번호를 입력하여 인증을 완료해주세요."
    from_email = settings.EMAIL_HOST_USER
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[email],
        fail_silently=False,
    )
    return verification_code

class CheckEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({"detail": "이미 존재하는 email입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        verification_code = send_verification_email(email)
        user, created = TemporaryUser.objects.get_or_create(email=email)
        user.code = verification_code
        user.save()            
        return Response({"detail": "사용 가능한 email입니다."}, status=status.HTTP_200_OK)
    
class ConfirmEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        user = TemporaryUser.objects.get(email=email)
        
        if user.is_expired:
            return Response({"detail": "인증 코드가 만료"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.code == code:
            user.is_certified = True
            user.save()
            return Response({"detail": "인증 성공"}, status=status.HTTP_200_OK)
        return Response({"detail": "인증 실패"}, status=status.HTTP_400_BAD_REQUEST)
       
class SigninView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email:
            return Response({"No email"}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"No password"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"No user"})
        
        if user.password != password:
            return Response({"Incoorrect password"}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "detail": "success",
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "로그아웃 성공"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "로그아웃 실패"}, status=status.HTTP_400_BAD_REQUEST)

def send_find_password_email(email):
    verification_code = str(random.randint(100000, 999999))
    
    subject = "SWANDA 비밀번호 찾기"
    message = f"SWANDA 비밀번호 찾기 확인 메일입니다.\n\n인증번호: {verification_code}\n\n해당 인증번호를 입력하여 인증을 완료해주세요."
    from_email = settings.EMAIL_HOST_USER
    
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[email],
        fail_silently=False,
    )
    return verification_code

class SendCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = TemporaryUser.objects.get(email=email)
        
        code = send_find_password_email(email)
        user.code = code
        user.save()
                
        return Response({"detail": "인증번호 전송 완료"}, status=status.HTTP_200_OK)
    
class FindPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        tem_user = TemporaryUser.objects.get(email=email)
        user = User.objects.get(email=email)
        print(tem_user.code)
        if tem_user.code == code:
            new_password = str(random.randint(10000000, 99999999))
            user.password=new_password
            user.save()
            return Response({
                "detail": f"비밀번호가 재설정되었습니다.",
                "password": f"{user.password}"
                }, status=status.HTTP_200_OK)
        
class CheckPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        password = request.data.get("password")
        
        if user.password == password:
            return Response({"detail": "일치"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "불일치"}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_class = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")
        
        if password1 != password2:
            return Response({"detail": "불일치"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.password = password1
            user.save()
            return Response({"detail": "변경 완료"}, status=status.HTTP_200_OK)
