from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    UserRegistrationView, 
    VerifyEmailView,
    UserProfileView,
    EmailDigestPreferenceView
)

# Define the app name for URL reversing
app_name = 'users'

urlpatterns = [
    # --- Step A: Registration and Verification ---
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify/', VerifyEmailView.as_view(), name='verify_email'), 

    # --- Step B: Login (JWT Authentication) ---
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Login/Get Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # --- Step C: Settings (Authenticated access required) ---
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('preferences/', EmailDigestPreferenceView.as_view(), name='user_preferences'),
]