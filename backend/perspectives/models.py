from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Perspective(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="perspective")

    def __str__(self):
        return f"Perspetiva do projeto {self.project.name}"


class PerspectiveQuestionBase(models.Model):
    question_text = models.TextField(unique=True)

    def __str__(self):
        return self.question_text


class PerspectiveQuestion(models.Model):
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name="questions")
    question = models.ForeignKey(PerspectiveQuestionBase, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("perspective", "question")

    def __str__(self):
        return self.question.question_text


class PerspectiveMember(models.Model):
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(PerspectiveQuestion, on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        unique_together = ("perspective", "user", "question")

    def __str__(self):
        return f"{self.user.username} - {self.question.question.question_text}: {self.value}"