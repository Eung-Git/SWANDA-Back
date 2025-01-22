from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken    
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

class SignupView(APIView):
    def post(self, request):
        print(request.data)
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
