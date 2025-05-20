# users/urls.py
from django.urls import path
from .views import RegisterView, CurrentUserView, CustomTokenObtainPairView
# 导入 Simple JWT 提供的视图
from rest_framework_simplejwt.views import (
    # TokenObtainPairView, # 注释掉，使用自定义的
    TokenRefreshView,  # 刷新 Token
    TokenVerifyView,   # 验证 Token (可选)
)
# from .views import CustomTokenObtainPairView # 如果你自定义了登录视图

app_name = 'users' # 定义 app namespace (可选但推荐)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # 使用自定义的登录视图
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 注释掉默认视图
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), # 可选
    path('me/', CurrentUserView.as_view(), name='current_user'), # 获取当前用户信息
]