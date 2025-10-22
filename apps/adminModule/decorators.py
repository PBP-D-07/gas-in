from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def admin_required(view_func):
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_admin:    
            return redirect('/')          
        return view_func(request, *args, **kwargs)
    return _wrapped_view
