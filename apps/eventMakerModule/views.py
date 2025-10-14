from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse
from apps.eventMakerModule.models import Event

def show_create(request):
    return render(request, "create_event.html")

def create_event(request):
    try:
        name = (request.POST.get("name"))                                                                                                                                                                                                                               
        description = (request.POST.get("description"))
        date = request.POST.get("date")
        location = request.POST.get("location")
        category = request.POST.get("category")
        thumbnail = request.POST.get("thumbnail")
        user = request.user

        new_event = Event.objects.create(
            name=name,
            description=description,
            date=date,
            location=location,
            thumbnail=thumbnail,
            category=category,
            user=user
        )
        
        data = model_to_dict(new_event)

        return JsonResponse({
            "message": "Product created successfully",
            "data": data
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
