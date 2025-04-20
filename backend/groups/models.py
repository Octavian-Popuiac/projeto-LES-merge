from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
# Create your models here.

User = get_user_model()

class GroupMetadata(models.Model):
  group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='metadata')
  description = models.TextField(blank=True)
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"GroupMetadata for {self.group.name}"