import json
import random
import os
from uuid import uuid4
from django.utils.dateparse import parse_datetime
from apps.venueModule.models import Venue, VenueImage, User

def run():
    with open('data/dataset_venue.json', 'r', encoding='utf-8') as f:
        venues_blob = json.load(f)

    if isinstance(venues_blob, dict) and 'data' in venues_blob:
        venues = venues_blob.get('data', [])
    else:
        venues = venues_blob

    infos = []
    with open('data/dataset_information_venue.json', 'r', encoding='utf-8') as f2:
        infos = json.load(f2)

    owner = User.objects.first()

    for index, v in enumerate(venues):
        info = infos[index] if index < len(infos) else {}

        owner = User.objects.first()

        description_str = (
            f"Luas Tanah: {v.get('luas_tanah', 'kosong')} m², "
            f"Luas Bangunan: {v.get('luas_bangunan', 'kosong')} m², "
            f"Luas Keseluruhan: {v.get('luas_keseluruhan', 'kosong')} m². "
            f"Periode Data: {v.get('periode_data', 'N/A')}."
        )
        thumbnail = info.get('thumbnail') if isinstance(info, dict) else ''
        images = info.get('images') if isinstance(info, dict) else []
        if not isinstance(images, list):
            images = [images] if images else []

        category = info.get('category') if isinstance(info, dict) else None
        allowed = {c[0] for c in Venue.CATEGORY_CHOICES}
        if category not in allowed:
            category = 'other'

        contact = v.get('contact_number') or None
        if not contact:
            length = random.randint(10, 12)
            remaining = length - 2
            contact = '08' + ''.join(random.choice('0123456789') for _ in range(remaining))
        contact = str(contact)[:12]

        venue = Venue.objects.create(
            id=uuid4(),
            name=v.get('nama_fasilitas') or 'Unnamed Venue',
            description=description_str,
            location=v.get('nama_fasilitas') or '',
            thumbnail=thumbnail or (images[0] if images else ''),
            category=category or 'other',
            contact_number=contact,
            owner=owner,
        )

        VenueImage.objects.filter(venue=venue).delete()
        final_images = []
        if thumbnail:
            final_images.append(thumbnail)
        for it in images:
            if it and it not in final_images:
                final_images.append(it)

        for i_img, img in enumerate(final_images):
            if not img:
                continue
            VenueImage.objects.create(venue=venue, image=img, order=i_img)

        print(f"✅ Added venue: {venue.name} (images: {len(final_images)})")