import json
import os
from uuid import uuid4
from django.utils.dateparse import parse_datetime
from django.core.files import File
from django.conf import settings
from apps.eventMakerModule.models import Event, User


def run():
    with open('data/events.json', 'r', encoding='utf-8') as f:
        events = json.load(f)

    owner = User.objects.filter(is_admin=False).first()

    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'event_thumbnails')

    thumbnail_files = []

    if os.path.exists(thumbnail_dir):
        thumbnail_files = [
            os.path.join(thumbnail_dir, f)
            for f in os.listdir(thumbnail_dir)
            if os.path.isfile(os.path.join(thumbnail_dir, f))
        ]
    else:
        print("⚠️ Folder media/event_thumbnails tidak ditemukan. Event tanpa thumbnail.")

    thumbnail_index = 0
    thumbnail_count = len(thumbnail_files)

    for e in events:
        event = Event(
            id=uuid4(),
            name=e['name'],
            description=e.get('description', 'No description available'),
            date=parse_datetime(e['date']),
            location=e['location'],
            category=e.get('category', 'other'),
            is_accepted=e.get('is_accepted', False),
            owner=owner,
        )

        if thumbnail_index < thumbnail_count:
            thumbnail_path = thumbnail_files[thumbnail_index]
            with open(thumbnail_path, 'rb') as img:
                event.thumbnail.save(
                    os.path.basename(thumbnail_path),
                    File(img),
                    save=False
                )
            thumbnail_index += 1
            print(f"🖼️ Thumbnail: {os.path.basename(thumbnail_path)}")

        event.save()
        print(f"✅ Added event: {event.name}")
