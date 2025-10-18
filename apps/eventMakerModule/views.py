from django.shortcuts import render 
from django.forms.models import model_to_dict
from django.conf import settings
from django.http import JsonResponse
from apps.eventMakerModule.models import Event

def show_create(request):
    return render(request, "create_event.html")

def show_edit(request, id):
    return render(request, "edit_event.html", {"event_id":id})

def create_event(request):
    if request.method != 'POST':
        return JsonResponse({
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
    
    for e in events:
        if e['thumbnail']:
            e['thumbnail'] = settings.MEDIA_URL + e['thumbnail']
    
    return JsonResponse({'message': 'All event retreived successfully', 'data': events})

def get_event_by_id(request, id):
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"message": "Event not found"}, status=404)
    
    event_dict = model_to_dict(event)
    if event.thumbnail:
        event_dict['thumbnail'] = settings.MEDIA_URL + str(event.thumbnail)
    
    return JsonResponse({"message": "Event retreived successfully", "data":event_dict}, status=200)

def delete_event(request, id):
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"message": "Event not found"}, status=404)
    
    event.delete()
    return JsonResponse({
        "message": "Event succesfully deleted"
    }, status=200)
    
def join_event(request, id):
    user = request.user
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"message": "Event not found"}, status=404)
    
    if event.participants.filter(id=request.user.id).exists():
        return JsonResponse({"message": "User already joined"}, status=400)
    
    event.participants.add(user)
    
    return JsonResponse({
        "message": f"{request.user.username} joined {event.name}",
        "data": {
            "event_id": str(event.id),
            "total_participants": event.participants.count()
        }
    }, status=200)
    
def edit_event(request, id): 
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"message": "Event not found"}, status=404)

    name = request.POST.get("name", event.name)
    description = request.POST.get("description", event.description)
    date = request.POST.get("date", event.date)
    location = request.POST.get("location", event.location)
    category = request.POST.get("category", event.category)
    thumbnail = request.FILES.get("thumbnail", event.thumbnail)

    event.name = name
    event.description = description
    event.date = date
    event.location = location
    event.category = category
    if thumbnail:
        event.thumbnail = thumbnail
    event.save()

    return JsonResponse({
        "message": "Event successfully updated",
        "data": {
            "id": str(event.id),
            "name": event.name,
            "description": event.description,
            "date": event.date,
            "location": event.location,
            "category": event.category,
            "thumbnail": event.thumbnail.url if event.thumbnail else None,
        }
    }, status=200)
