from django.contrib.auth.models import AbstractUser, Group
from django.shortcuts import get_object_or_404
from django.db import transaction
from . import models


class BaseUser(AbstractUser):
    def save(self):
        with transaction.atomic():
            admin_group = get_object_or_404(Group, name="administrator")
            local_group = get_object_or_404(Group, name="buyer")
            if self.is_superuser and admin_group:
                self.groups.add(admin_group)
            else:
                self.groups.add(local_group)
            super().save(self)
            
            if not self.is_superuser:
                models.User.objects.create(user=self.pk, first_name=self.first_name, last_name=self.last_name)
