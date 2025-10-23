import datetime
from django.shortcuts import render, redirect, get_object_or_404
# from main.forms import ProductForm
from apps.venueModule.models import Venue
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags

def show_venue(request):
    venue_list = Venue.objects.all()

    context = {
        'venue_list': venue_list
    }

    return render(request, 'venue.html', context)

def venue_detail(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)

    context = {
        'venue': venue
    }

    return render(request, "venue_detail.html", context)

































# mengembalikan data dalam bentuk XML
def show_xml_venue(request):
    venue_list = Venue.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")

# mengembalikan data dalam bentuk JSON
def show_json_venue(request):
    venue_list = Venue.objects.prefetch_related('images').all()
    data = []
    for venue in venue_list:
        images = [img.image for img in venue.images.all()]
        data.append({
            'id': str(venue.id),
            'name': venue.name,
            'description': venue.description,
            'location': venue.location,
            'thumbnail': venue.thumbnail,
            'images': images,
            'contact_number': venue.contact_number,
            'owner_username': venue.owner.username if venue.owner else None,
            'category': venue.category,
            'created_at': venue.created_at.isoformat(),
            'owner_id': venue.owner_id,
        })

    return JsonResponse(data, safe=False)

# mengembalikan data dalam bentuk XML berdasarkan ID
def show_xml_by_id_venue(request, venue_id):
    try:
        venue_item = Venue.objects.filter(pk=venue_id)
        xml_data = serializers.serialize("xml", venue_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Venue.DoesNotExist:
        return HttpResponse(status=404)

# mengembalikan data dalam bentuk JSON berdasarkan ID
def show_json_by_id_venue(request, venue_id):
    try:
        venue = Venue.objects.prefetch_related('images').get(pk=venue_id)
        images = [img.image for img in venue.images.all()]
        data = {
            'id': str(venue.id),
            'name': venue.name,
            'description': venue.description,
            'location': venue.location,
            'thumbnail': venue.thumbnail,
            'images': images,
            'contact_number': venue.contact_number,
            'owner_username': venue.owner.username if venue.owner else None,
            'category': venue.category,
            'created_at': venue.created_at.isoformat(),
            'owner_id': venue.owner_id,
        }
        return JsonResponse(data)
    except Venue.DoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=404)