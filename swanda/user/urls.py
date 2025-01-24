from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
# router.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('checknickname/', CheckNicknameView.as_view(), name='checknickname'),
    path('checkemail/', CheckEmailView.as_view(), name='checkemail'),
    path('confirmemail/', ConfirmEmailView.as_view(), name='confirmemail'),
    path('sendcode/', SendCodeView.as_view(), name='sendcode'),
    path('findpassword/', FindPasswordView.as_view(), name='findpassword'),
    path('checkpassword/', CheckPasswordView.as_view(), name='checkpassword'),
    path('changepassword/', ChangePasswordView.as_view(), name='changepassword'),
]
