from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse
from apps.eventMakerModule.models import Event

def show_create(request):
    return render(request, "create_event.html")

def create_event(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'}, status=405)
    try:
        name = request.POST.get("name")                                                                                                                                                                                                                            
        description = request.POST.get("description")
        date = request.POST.get("date")
        location = request.POST.get("location")
        category = request.POST.get("category")
        thumbnail = request.FILES.get("thumbnail")
        owner = request.user

        new_event = Event.objects.create(
            name=name,
            description=description,
            date=date,
            location=location,
            category=category,
            thumbnail=thumbnail,
            owner=owner
        )
        
        data = model_to_dict(new_event)

        data["thumbnail"] = new_event.thumbnail.url if new_event.thumbnail else ""
        
        return JsonResponse({
            "message": "Event created successfully",
            "data": data
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_all_event(request):
    events = list(Event.objects.values(
        'id', 'name', 'description', 'date', 'location', 'category', 'thumbnail', 'owner'
    ))
    return JsonResponse({'success': True, 'data': events}, safe=False)

def delete_event(request, id):
    event = Event.objects.filter(pk=id)
    
    if not event:
        return JsonResponse({
            "message": "Event not found",
        }, status=404)
        
    event.delete()
    return JsonResponse({
        "message": "Event succesfully deleted"
    }, status=200)
