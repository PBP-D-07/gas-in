from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Event
from django.views.decorators.csrf import csrf_exempt
from .decorators import admin_required

@admin_required
def dashboard(request):
    # Pisahkan events berdasarkan status
    pending_events = Event.objects.filter(is_accepted=None).order_by('-created_at')
    approved_events = Event.objects.filter(is_accepted=True).order_by('-created_at')
    rejected_events = Event.objects.filter(is_accepted=False).order_by('-created_at')
    
    context = {
        'pending_events': pending_events,
        'approved_events': approved_events,
        'rejected_events': rejected_events,
        'pending_count': pending_events.count(),
        'approved_count': approved_events.count(),
        'rejected_count': rejected_events.count(),
    }
    
    return render(request, 'admin_homepage.html', context)

@csrf_exempt
def update_event_status(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        status = request.POST.get('status')

        if status == 'approve':
            event.is_accepted = True
        elif status == 'reject':
            event.is_accepted = False
        elif status == 'pending':
            event.is_accepted = None  # Revoke approval

        event.save()
        return JsonResponse({'success': True, 'status': status})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@csrf_exempt
def delete_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        
        # Hanya bisa delete yang rejected
        if event.is_accepted == False:
            event.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Can only delete rejected events'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)