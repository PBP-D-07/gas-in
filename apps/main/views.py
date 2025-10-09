from django.shortcuts import render
from django.http import JsonResponse
from apps.main.models import User

# Create your views here.
def show_main(request):
    return render(request, 'main.html')

def register(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'}, status=405)

    username = request.POST.get('username', '').strip()
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')

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

    # Cek apakah username sudah ada
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'success': False,
            'message': 'Username already exists.'
        }, status=409)

    # Buat akun baru
    user = User.objects.create_user(username=username, password=password1)
    return JsonResponse({
        'success': True,
        'message': 'Account created successfully!',
        'data': {
            'username': user.username,
            'id': user.id # type: ignore
        }
    }, status=201)