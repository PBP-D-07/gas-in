from django.shortcuts import render

def show_venue(request):
    return render(request, 'venue.html')

def venue_detail(request, venue_id):
    return render(request, 'venue_detail.html', {'venue_id': venue_id})