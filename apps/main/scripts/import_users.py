# import json
# from uuid import uuid4
# from django.utils.dateparse import parse_datetime
# from apps.eventMakerModule.models import User

# def run():
#     with open('data/users.json', 'r', encoding='utf-8') as f:
#         users = json.load(f)

#     for u in users:
#         user = User.objects.create(
#             id=uuid4(),
#             username=u['username'],
#             password=u['password']
#         )
#         print(f"✅ Added user: {user.username}")

import json
from uuid import uuid4
from apps.eventMakerModule.models import User

def run():
    with open('data/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    for u in users:
        user = User(
            id=uuid4(),
            username=u['username'],
            password=u['password'],
            is_admin=u.get('is_admin', False)
        )
        user.set_password(u['password'])  
        user.save()

        print(f"✅ Added user: {user.username}")
