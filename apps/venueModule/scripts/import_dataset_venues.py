import json
from uuid import uuid4
from django.utils.dateparse import parse_datetime
from apps.venueModule.models import Venue, User

def run():
    with open('data/dataset_venue.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    owner = User.objects.first()

    for v in venues:
        description_str = (
            
            f"Luas Tanah: {v.get('luas_tanah', 'kosong')} m², "
            f"Luas Bangunan: {v.get('luas_bangunan', 'kosong')} m², "
            f"Luas Keseluruhan: {v.get('luas_keseluruhan', 'kosong')} m². "
            f"Periode Data: {v.get('periode_data', 'N/A')}."
        )
        venue = Venue.objects.create(
            id=uuid4(),
            name=v['nama_fasilitas'],
            description=description_str,
            location=v['nama_fasilitas'],
            thumbnail=v.get('thumbnail', ''),
            category=v.get('category', 'other'),
            is_accepted=v.get('is_accepted', False),
            contact_number=v.get('contact_number', ''),
            owner=owner,
        )
        print(f"✅ Added venue: {venue.name}")