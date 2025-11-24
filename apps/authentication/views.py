from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from apps.main.models import User
import json

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']

        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        
        return JsonResponse({
            "username": user.username,
            "status": 'success',
            "message": "User created successfully!"
        }, status=200)
    
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)

    try:
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
        else :
            data = request.POST

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({
                "status": False,
                "message": "Username and password are required."
            }, status=400)

        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({
                "status": False,
                "message": "Login failed, please check your username or password."
            }, status=401)

        if not user.is_active:
            return JsonResponse({
                "status": False,
                "message": "Your account is disabled."
            }, status=401)

        auth_login(request, user)

        response = JsonResponse({
            "status": True,
            "message": "Login successful!",
            "username": user.username,
            "is_admin": user.is_admin,  
        })

        response.set_cookie(
            key='sessionid',
            value=request.session.session_key,
            httponly=True,
            samesite='None',
            secure=True
        )

        return response

    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Error: {str(e)}"
        }, status=500)
