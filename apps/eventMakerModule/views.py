from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.conf import settings
from django.http import JsonResponse
from apps.eventMakerModule.models import Event
from django.utils import timezone
from datetime import datetime

def show_create(request):
    return render(request, "create_event.html")

def show_edit(request, id):
    return render(request, "edit_event.html", {"event_id":id})

def show_detail(request, id):
    return render(request, "event_detail.html", {"event_id":id})

@csrf_exempt
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
        date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M")
        aware_date = timezone.make_aware(date_obj, timezone.get_current_timezone())
        
        if not owner.is_authenticated:
            return JsonResponse({"message": "You must be logged in to create an event"}, status=401)

        new_event = Event.objects.create(
            name=name,
            description=description,
            date=aware_date,
            location=location,
            category=category,
            thumbnail=thumbnail,
            owner=owner
        )
        
        event_dict = model_to_dict(new_event, exclude=['owner', 'thumbnail'])
        event_dict['id'] = str(new_event.id)
        event_dict['owner'] = {
            "id": new_event.owner.id,  #type:ignore
            "username": new_event.owner.username,  #type:ignore
        }
        event_dict['thumbnail'] = settings.MEDIA_URL + str(new_event.thumbnail) if new_event.thumbnail else None
        
        new_event.save()
        
        return JsonResponse({
                "message": "Event created successfully",
                "data": event_dict
            }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_all_event(request):
    events = Event.objects.all()
    data = []

    for e in events:
        e_dict = {
            'id': e.id,
            'name': e.name,
            'description': e.description,
            'date': e.date,
            'location': e.location,
            'category': e.category,
            'category_display': e.get_category_display(),  # type: ignore
            'thumbnail': settings.MEDIA_URL + str(e.thumbnail) if e.thumbnail else None,
            'owner': e.owner.id if e.owner else None,
        }
        data.append(e_dict)

    return JsonResponse({'message': 'All events retrieved successfully', 'data': data}, status=200)


def get_event_by_id(request, id):
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"message": "Event not found"}, status=404)

    event_dict = model_to_dict(event, exclude=['owner', 'participants', 'thumbnail'])
    event_dict['id'] = str(event.id)
    event_dict['category_display'] = event.get_category_display() #type: ignore
    event_dict['owner'] = {
        "id": event.owner.id, #type: ignore
        "username": event.owner.username, #type: ignore
    }
    event_dict['participants'] = [
        {
            "id": p.id,
            "username": p.username,
        }
        for p in event.participants.all()
    ]
    event_dict['thumbnail'] = settings.MEDIA_URL + str(event.thumbnail) if event.thumbnail else None

    return JsonResponse({"message": "Event retrieved successfully", "data": event_dict}, status=200)

@csrf_exempt
def delete_event(request, id):
    if request.method != 'POST':
        return JsonResponse({
            'message': 'Invalid request method.'}, status=405)
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"message": "Event not found"}, status=404)
    
    event.delete()
    return JsonResponse({
        "message": "Event succesfully deleted"
    }, status=200)
    
@csrf_exempt
def join_event(request, id):
    if request.method != 'POST':
        return JsonResponse({
            'message': 'Invalid request method'}, status=405)

    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"message": "You must be logged in to join an event."}, status=401)
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"message": "Event not found"}, status=404)
    
    if event.participants.filter(id=request.user.id).exists():
        return JsonResponse({"message": "User already joined"}, status=400)
    
    event.participants.add(user)
    participants = [
        {
            "id": p.id,
            "username": p.username,
        }
        for p in event.participants.all()
    ]
    
    return JsonResponse({
        "message": f"{request.user.username} joined {event.name}",
        "data": {
            "event_id": str(event.id),
            "total_participants": event.participants.count(),
            "participants": participants
        }
    }, status=200)
    
@csrf_exempt
def edit_event(request, id): 
    if request.method != 'POST':
        return JsonResponse({
            'message': 'Invalid request method'}, status=405)
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
