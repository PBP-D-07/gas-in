from django.core.management.base import BaseCommand
from apps.main.models import User

class Command(BaseCommand):
    help = 'Make a user admin by username'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to make admin')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        
        try:
            user = User.objects.get(username=username)
            
            if user.is_admin:
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" is already an admin!')
                )
                return
            
            user.is_admin = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully made "{username}" an admin!')
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist!')
            )