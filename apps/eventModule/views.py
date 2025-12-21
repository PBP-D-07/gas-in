from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.eventMakerModule.models import Event
from apps.eventModule.models import SavedSearch
import json

def show_discover(request):
    """Halaman discovery event dengan filter"""
    return render(request, "discover_events.html")

def show_saved_searches(request):
    """Halaman saved searches"""
    return render(request, "saved_searches.html")

def get_filtered_events(request):
    """API untuk mendapatkan event dengan filter"""
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
        try: 
            e_dict = {
                'id': str(e.id),
                'name': e.name,
                'description': e.description,
                'date': e.date.strftime('%Y-%m-%d %H:%M:%S') if e.date else None,
                'location': e.location,
                'category': e.category,
                'category_display': e.get_category_display() if hasattr(e, 'get_category_display') else e.category,  # type: ignore
                'thumbnail': e.thumbnail.url if e.thumbnail else None,
                'owner': {
                    'id': str(e.owner.id) if e.owner else None,
                    'username': e.owner.username if e.owner else None,
                },
                'participants_count': e.participants.count(),
            }
            data.append(e_dict)
        except Exception as err:
            print(f"Error processing event {e.id}: {err}")
            continue
    
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
    """API untuk mendapatkan opsi filter yang tersedia"""
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

@csrf_exempt
@require_http_methods(["POST"])
def create_saved_search(request):
    """Create saved search"""
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Authentication required'}, status=401)
    
    try:
        # Try to parse JSON from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to get data from POST
            data = {
                'name': request.POST.get('name'),
                'location': request.POST.get('location', ''),
                'category': request.POST.get('category', '')
            }
        
        name = data.get('name')
        location = data.get('location', '') or ''
        category = data.get('category', '') or ''
        
        # Validation
        if not name or not name.strip():
            return JsonResponse({'message': 'Name is required'}, status=400)
        
        # Create saved search with proper null handling
        saved_search = SavedSearch.objects.create(
            user=request.user,
            name=name.strip(),
            location=location.strip() if location else '',
            category=category.strip() if category else ''
        )
        
        return JsonResponse({
            'message': 'Saved search created successfully',
            'status': 'success',
            'data': {
                'id': str(saved_search.id),
                'name': saved_search.name,
                'location': saved_search.location or '',
                'category': saved_search.category or '',
                'created_at': saved_search.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=201)
        
    except Exception as e:
        print(f"Error pada create_saved_search: {str(e)}")
        import traceback
        traceback.print_exc()  # This will print full error stack
        return JsonResponse({
            'message': 'Failed to create saved search',
            'error': str(e)
        }, status=500)
    
@csrf_exempt
#@login_required
def get_saved_searches(request):
    """Get all saved searches for current user"""
    if not request.user.is_authenticated:
            return JsonResponse({'message': 'Authentication required'}, status=401)
    
    saved_searches = SavedSearch.objects.filter(user=request.user)
    
    data = []
    for ss in saved_searches:
        data.append({
            'id': str(ss.id),
            'name': ss.name,
            'location': ss.location,
            'category': ss.category,
            'created_at': ss.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({
        'message': 'Saved searches retrieved successfully',
        'data': data
    }, status=200)


@csrf_exempt
# @login_required
def get_saved_search_by_id(request, id):
    """Get saved search by ID"""
    if not request.user.is_authenticated:
            return JsonResponse({'message': 'Authentication required'}, status=401)
    
    try:
        saved_search = SavedSearch.objects.get(pk=id, user=request.user)
        
        return JsonResponse({
            'message': 'Saved search retrieved successfully',
            'data': {
                'id': str(saved_search.id),
                'name': saved_search.name,
                'location': saved_search.location,
                'category': saved_search.category,
                'created_at': saved_search.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=200)
    except SavedSearch.DoesNotExist:
        return JsonResponse({'message': 'Saved search not found'}, status=404)

@csrf_exempt
# @login_required
@require_http_methods(["POST"])
def update_saved_search(request, id):
    """Update saved search"""
    if not request.user.is_authenticated:
            return JsonResponse({'message': 'Authentication required'}, status=401)
    
    try:
        saved_search = SavedSearch.objects.get(pk=id, user=request.user)
        
        data = json.loads(request.body)
        saved_search.name = data.get('name', saved_search.name)
        saved_search.location = data.get('location', saved_search.location)
        saved_search.category = data.get('category', saved_search.category)
        saved_search.save()
        
        return JsonResponse({
            'message': 'Saved search updated successfully',
            'data': {
                'id': str(saved_search.id),
                'name': saved_search.name,
                'location': saved_search.location,
                'category': saved_search.category,
            }
        }, status=200)
    except SavedSearch.DoesNotExist:
        return JsonResponse({'message': 'Saved search not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
# @login_required
@require_http_methods(["POST"])
def delete_saved_search(request, id):
    """Delete saved search"""
    if not request.user.is_authenticated:
            return JsonResponse({'message': 'Authentication required'}, status=401)
    
    try:
        saved_search = SavedSearch.objects.get(pk=id, user=request.user)
        saved_search.delete()
        
        return JsonResponse({
            'message': 'Saved search deleted successfully'
        }, status=200)
    except SavedSearch.DoesNotExist:
        return JsonResponse({'message': 'Saved search not found'}, status=404)