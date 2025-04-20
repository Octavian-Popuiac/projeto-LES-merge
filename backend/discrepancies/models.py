from django.db import models
from projects.models import Project
from examples.models import Example


class Discrepancy(models.Model):
    STATUS_CHOICES = [
        ("unresolved", "Unresolved"),
        ("resolved", "Resolved"),
    ]

    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="discrepancies")
    example = models.ForeignKey(Example, on_delete=models.CASCADE, related_name="discrepancies", null=True)


    labels = models.JSONField(
        default=list)  # Lista de dicionários com label e contagem, ex: [{"label": "positive", "count": 3}, ...]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unresolved")

    def __str__(self):
        return f"Discrepancy: Example {self.example.id} with labels {self.labels}"
