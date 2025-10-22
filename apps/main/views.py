from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.main.models import User
from django.forms.models import model_to_dict
import json

# Create your views here.
def show_main(request):
    return render(request, 'main.html')

def show_login(request):
    return render(request, 'login.html')

@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'}, status=405)

    username = request.POST.get('username', '').strip()
    password1 = request.POST.get('password1', '').strip()
    password2 = request.POST.get('password2', '').strip()

    if not all([username, password1, password2]):
        return JsonResponse({
            'success': False,
            'message': 'All fields are required.'
        }, status=400)

    if password1 != password2:
        return JsonResponse({
            'success': False,
            'message': 'Passwords do not match.'
        }, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'success': False,
            'message': 'Username already exists.'
        }, status=409)

    user = User.objects.create_user(username=username, password=password1)
    data = model_to_dict(user)
    return JsonResponse({
        'success': True,
        'message': 'Account created successfully!',
        'data': {
            'username': user.username,
            'id': user.id # type: ignore
        }
    }, status=201)

@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'}, status=405)

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        response = JsonResponse({
            'success': True,
            'message': 'Login successful!',
        })
        return response
    else:
        return JsonResponse({'success': False, 'message': 'Invalid username or password.'})
    
def logout_user(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            logout(request)   
            return JsonResponse({"message": "Logout successful"}, status=200)
        else:
            return JsonResponse({"message": "You are not logged in"}, status=401)
    else:
        return JsonResponse({"message": "Method not allowed"}, status=405)

def get_all_user(request):
    users = list(User.objects.values(
        'id', 'username', 'is_admin', 'created_at'
    ))
    return JsonResponse({'success': True, 'data': users}, safe=False)
