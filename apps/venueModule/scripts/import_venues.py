import json
from uuid import uuid4
from django.utils.dateparse import parse_datetime
from apps.venueModule.models import Venue, User

def run():
    with open('data/venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    owner = User.objects.first()

    for v in venues:
        venue = Venue.objects.create(
            id=uuid4(),
            name=v['name'],
            description=v.get('description', 'No description available'),
            location=v['location'],
            thumbnail=v.get('thumbnail', ''),
            category=v.get('category', 'other'),
            is_accepted=v.get('is_accepted', False),
            owner=owner,
        )
        print(f"✅ Added venue: {venue.name}")