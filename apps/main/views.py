from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import requests
from apps.main.models import User
from django.forms.models import model_to_dict
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.main.models import User

@csrf_exempt
def promote_to_admin(request):
    """
    API untuk promote user jadi admin.
    Hanya bisa diakses oleh admin yang sudah ada.
    """
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    
    # Cek apakah yang request adalah admin
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You must be logged in'}, status=401)
    
    if not request.user.is_admin:
        return JsonResponse({'message': 'Only admins can promote users'}, status=403)
    
    username = request.POST.get('username', '').strip()
    
    if not username:
        return JsonResponse({'message': 'Username is required'}, status=400)
    
    try:
        user = User.objects.get(username=username)
        
        if user.is_admin:
            return JsonResponse({
                'message': f'{username} is already an admin'
            }, status=200)
        
        user.is_admin = True
        user.save()
        
        return JsonResponse({
            'message': f'{username} is now an admin!',
            'data': {
                'username': user.username,
                'is_admin': user.is_admin
            }
        }, status=200)
        
    except User.DoesNotExist:
        return JsonResponse({
            'message': f'User "{username}" not found'
        }, status=404)


@csrf_exempt
def demote_from_admin(request):
    """
    API untuk demote admin jadi user biasa.
    Hanya bisa diakses oleh admin yang sudah ada.
    """
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You must be logged in'}, status=401)
    
    if not request.user.is_admin:
        return JsonResponse({'message': 'Only admins can demote users'}, status=403)
    
    username = request.POST.get('username', '').strip()
    
    if not username:
        return JsonResponse({'message': 'Username is required'}, status=400)
    
    # Prevent self-demotion
    if request.user.username == username:
        return JsonResponse({
            'message': 'You cannot demote yourself!'
        }, status=400)
    
    try:
        user = User.objects.get(username=username)
        
        if not user.is_admin:
            return JsonResponse({
                'message': f'{username} is not an admin'
            }, status=200)
        
        user.is_admin = False
        user.save()
        
        return JsonResponse({
            'message': f'{username} has been demoted to regular user',
            'data': {
                'username': user.username,
                'is_admin': user.is_admin
            }
        }, status=200)
        
    except User.DoesNotExist:
        return JsonResponse({
            'message': f'User "{username}" not found'
        }, status=404)

def show_main(request):
    return render(request, 'main.html')

def show_login(request):
    return render(request, 'login.html')

def show_register(request):
    return render(request, 'register.html')

@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({
            'message': 'Invalid request method'
        }, status=405)

    username = request.POST.get('username', '').strip()
    password1 = request.POST.get('password1', '').strip()
    password2 = request.POST.get('password2', '').strip()

    if not all([username, password1, password2]):
        return JsonResponse({
            'message': 'All fields are required'
        }, status=400)

    if password1 != password2:
        return JsonResponse({
            'message': 'Passwords do not match'
        }, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'message': 'Username already exists'
        }, status=409)

    user = User.objects.create_user(username=username, password=password1)

    data = model_to_dict(user, fields=['id', 'username', 'email', 'is_active'])
    
    return JsonResponse({
        'message': 'Account created successfully!',
        'data': data
    }, status=201)

@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)

        if user.is_admin: #type: ignore
            return JsonResponse({
                'message': 'Login successful!',
                'redirect_url': '/admin/'
            }, status=200)
        else:
            return JsonResponse({
                'message': 'Login successful!',
                'redirect_url': '/'
            }, status=200)
    else:
        return JsonResponse({'message': 'Invalid username or password'}, status=401)


@csrf_exempt
def logout_user(request):
    if request.method != 'POST':
        return JsonResponse({
            'message': 'Invalid request method'}, status=405)

    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({
            'message': 'Logout successful'
        }, status=200)
    else:
        return JsonResponse({
            'message': 'You are not logged in'
        }, status=401)


def get_all_user(request):
    if request.method != 'GET':
        return JsonResponse({
            'message': 'Invalid request method'
        }, status=405)

    users = list(User.objects.values(
        'id', 'username', 'is_admin', 'created_at'
    ))
    return JsonResponse({
        'data': users
    }, status=200)

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)