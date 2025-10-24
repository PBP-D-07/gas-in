from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from apps.eventMakerModule.models import Event

def show_discover(request):
    return render(request, "events_filter.html")

def get_filtered_events(request):
    # Ambil semua event yang sudah diterima
    events = Event.objects.filter(is_accepted=True)
    
    # Filter berdasarkan lokasi
    location = request.GET.get('location', '').strip()
    if location:
        # Filter lokasi case-insensitive
        events = events.filter(location__icontains=location)
    
    # Filter berdasarkan kategori olahraga
    category = request.GET.get('category', '').strip()
    if category:
        events = events.filter(category=category)
    
    # Format data untuk response
    data = []
    for e in events:
        e_dict = {
            'id': str(e.id),
            'name': e.name,
            'description': e.description,
            'date': e.date.strftime('%Y-%m-%d %H:%M:%S') if e.date else None,
            'location': e.location,
            'category': e.category,
            'category_display': e.get_category_display(),  
            'thumbnail': settings.MEDIA_URL + str(e.thumbnail) if e.thumbnail else None,
            'owner': {
                'id': e.owner.id if e.owner else None,
                'username': e.owner.username if e.owner else None,
            },
            'participants_count': e.participants.count(),
        }
        data.append(e_dict)
    
    return JsonResponse({
        'message': 'Events retrieved successfully',
        'data': data,
        'total': len(data),
        'filters_applied': {
            'location': location if location else None,
            'category': category if category else None,
        }
    }, status=200)

def get_filter_options(request):
    # Lokasi JABODETABEK
    locations = [
        'Jakarta',
        'Bogor',
        'Depok',
        'Tangerang',
        'Bekasi'
    ]
    
    # Kategori dari model Event
    categories = [
        {'value': 'running', 'label': 'Lari'},
        {'value': 'badminton', 'label': 'Badminton'},
        {'value': 'futsal', 'label': 'Futsal'},
        {'value': 'football', 'label': 'Sepak Bola'},
        {'value': 'basketball', 'label': 'Basket'},
        {'value': 'cycling', 'label': 'Sepeda'},
        {'value': 'volleyball', 'label': 'Voli'},
        {'value': 'yoga', 'label': 'Yoga'},
        {'value': 'padel', 'label': 'Padel'},
        {'value': 'other', 'label': 'Lainnya'},
    ]
    
    return JsonResponse({
        'message': 'Filter options retrieved successfully',
        'data': {
            'locations': locations,
            'categories': categories
        }
    }, status=200)