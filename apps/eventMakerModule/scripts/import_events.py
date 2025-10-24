import json
from uuid import uuid4
from django.utils.dateparse import parse_datetime
from apps.eventMakerModule.models import Event, User

def run():
    with open('data/events.json', 'r', encoding='utf-8') as f:
        events = json.load(f)

    owner = User.objects.filter(is_admin=False).first()

    for e in events:
        event = Event.objects.create(
            id=uuid4(),
            name=e['name'],
            description=e.get('description', 'No description available'),
            date=parse_datetime(e['date']),
            location=e['location'],
            category=e.get('category', 'other'),
            is_accepted=e.get('is_accepted', False),
            owner=owner,
        )
        print(f"✅ Added event: {event.name}")
