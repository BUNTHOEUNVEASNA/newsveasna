from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer, 
    EmailDigestPreferenceSerializer
)
from .models import EmailVerificationToken, EmailDigestPreference

User = get_user_model()

# --- Utility Function ---

def send_verification_email(user, token):
    """Sends a verification email to the user with the generated token."""
    # Construct the full verification URL for the frontend
    verification_link = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    subject = 'Activate Your News Scraper Account'
    
    # Render the HTML template for the email content
    html_message = render_to_string('email/verification_email.html', {
        'username': user.username, 
        'verification_link': verification_link
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    # Send the email
    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
    except Exception as e:
        print(f"ERROR: Could not send verification email to {user.email}: {e}")


# --- API Views ---

class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration (Step A).
    Creates a new inactive user, initializes preferences, and sends verification email.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        # 1. Create the inactive user
        user = serializer.save()
        
        # 2. Create the verification token
        try:
            token_obj = EmailVerificationToken.objects.create(user=user)
            # 3. Send the email (handled by utility function)
            send_verification_email(user, token_obj.token)
        except IntegrityError:
            print(f"ERROR: Failed to create token for user {user.username}")
            pass
        
        # 4. Initialize default preferences for the user (MANDATORY for OneToOne relationship)
        EmailDigestPreference.objects.create(user=user)


class VerifyEmailView(generics.GenericAPIView):
    """
    API view to handle the email verification link click (Step A).
    Activates the user's account if the token is valid.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Expects the verification token in the request body
        token = request.data.get('token')

        if not token:
            return Response({"detail": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the token object
            token_obj = get_object_or_404(EmailVerificationToken, token=token)
            user = token_obj.user
            
            if user.is_active:
                 return Response({"detail": "Email already verified. Account is active."}, status=status.HTTP_200_OK)

            if token_obj.is_expired():
                # Delete expired token and suggest resend
                token_obj.delete()
                return Response({"detail": "Verification link has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            # Activate the user
            user.is_active = True
            user.save()
            
            # Delete the token after successful use
            token_obj.delete()

            return Response({"detail": "Email successfully verified. Account is now active."}, status=status.HTTP_200_OK)

        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid or already used token."}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view to view and update user profile details (Step C).
    Permission: IsAuthenticated.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Returns the currently authenticated user
        return self.request.user


class EmailDigestPreferenceView(generics.RetrieveUpdateAPIView):
    """
    API view to view and update email digest preferences (Step C).
    Permission: IsAuthenticated.
    """
    serializer_class = EmailDigestPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve or create the preferences object for the authenticated user
        user = self.request.user
        return EmailDigestPreference.objects.get_or_create(user=user)[0]