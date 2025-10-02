"""
Idempotent command to create default hospital groups.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps


DEFAULT_GROUPS = [
    "Admin",
    "Doctor",
    "Nurse",
    "Pharmacist",
    "Lab",
    "Reception",
]


class Command(BaseCommand):
    help = "Create default groups for AfyaAccess and optionally assign base permissions."

    def handle(self, *args, **options):
        for name in DEFAULT_GROUPS:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group: {name}"))
            else:
                self.stdout.write(f"Group already exists: {name}")

        # Example: attach basic users-model permissions to Admin group.
        try:
            admin_group = Group.objects.get(name="Admin")
            perms = Permission.objects.filter(
                content_type__app_label="users",
                codename__in=["add_user", "change_user", "delete_user", "view_user"],
            )
            admin_group.permissions.add(*perms)
            self.stdout.write(self.style.SUCCESS("Assigned user model permissions to Admin group."))
        except Exception as exc:
            # If anything fails, print message but do not crash.
            self.stdout.write(self.style.WARNING("Could not assign user perms automatically: " + str(exc)))

        self.stdout.write(self.style.SUCCESS("init_groups complete."))
