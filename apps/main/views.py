from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.main.models import User
from django.forms.models import model_to_dict
import json
from django.core import serializers

# Create your views here.
def show_main(request):
    return render(request, 'main.html')

@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)

    username = data.get('username', '').strip()
    password1 = data.get('password1', '').strip()
    password2 = data.get('password2', '').strip()

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

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
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
    
def get_all_user(request):
    users = list(User.objects.values(
        'id', 'username', 'is_admin', 'created_at'
    ))
    return JsonResponse({'success': True, 'data': users}, safe=False)