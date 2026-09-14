from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(pk=4)
        group, created = Group.objects.get_or_create(
            name="profile_manager"
        )
        permisson_profile = Permission.objects.get(
            codename="view_profile"
        )
        permisson_logentry = Permission.objects.get(
            codename="view_logentry"
        )

        group.permissions.add(permisson_profile)

        user.groups.add(group)

        user.user_permissions.add(permisson_logentry)

        group.save()
        user.save()