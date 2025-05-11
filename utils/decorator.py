from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def unblocked_user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_blocked:
            return redirect(reverse('blocked_page'))
        return view_func(request, *args, **kwargs)
    return wrapper