from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if request.user.is_authenticated:
            return

        email = sociallogin.user.email
        if not email:
            return

        User = get_user_model()
        try:
            existing_user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)

        if not user.username:
            user.username = user.email or str(user.id)

        if not user.username:
            user.username = str(user.id)

        user.save()
        return user

    def get_login_redirect_url(self, request):
        if request.user.is_authenticated and not hasattr(request.user, 'profile'):
            return reverse('accounts:choose_role')
        return super().get_login_redirect_url(request)
