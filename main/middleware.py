from django.shortcuts import redirect
from django.urls import reverse

class OnboardingMiddleware:
 def __init__(self, get_response):
  self.get_response = get_response

 def __call__(self, request):
  user = request.user

  if user.is_authenticated:
   profile = getattr(user, 'profile', None)

   # jika belum onboarding → cegah akses halaman lain
   onboarding_paths = [
    reverse('onboard_wallet'),
    reverse('onboard_income'),
    reverse('onboard_expense'),
   ]

   if profile and not profile.is_onboarded:
    if request.path not in onboarding_paths:
     return redirect('onboard_wallet')

  return self.get_response(request)
