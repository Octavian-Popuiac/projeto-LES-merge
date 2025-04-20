from rest_framework import generics, permissions
from .models import Perspective
from .serializers import PerspectiveSerializer
from projects.models import Project


class PerspectiveCreateView(generics.CreateAPIView):
    queryset = Perspective.objects.all()
    serializer_class = PerspectiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        # Só permite se o user for admin do projeto
        #if self.request.user != project.admin:  # ajusta conforme o teu modelo
        #    raise PermissionError("Apenas o admin do projeto pode criar a perspetiva.")
        serializer.save()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from labels.models import Category
from .models import PerspectiveMember

class LabelsWithPerspectiveAnswersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, example_id):
        from projects.models import Project
        from examples.models import Example
        from .models import Perspective
        from labels.models import Category

        try:
            project = Project.objects.get(id=project_id)
            example = Example.objects.get(id=example_id, project=project)
            perspective = Perspective.objects.get(project=project)
        except (Project.DoesNotExist, Example.DoesNotExist, Perspective.DoesNotExist):
            return Response({"detail": "Dados inválidos."}, status=404)

        labels = Category.objects.filter(example=example)

        result = []

        for label in labels:
            user = label.user

            answers = []
            for question in perspective.questions.all():
                try:
                    member = PerspectiveMember.objects.get(
                        perspective=perspective,
                        user=user,
                        question=question
                    )
                    value = member.value
                except PerspectiveMember.DoesNotExist:
                    value = "No answer"

                answers.append({
                    "question": question.question.question_text,
                    "answer": value
                })

            result.append({
                "label": label.label.text,
                "user": user.username,
                "question_answers": answers
            })

        return Response(result)

from rest_framework.generics import RetrieveAPIView
from .models import Perspective
from .serializers import PerspectiveSerializer

class PerspectiveByProjectView(RetrieveAPIView):
    serializer_class = PerspectiveSerializer
    lookup_field = "project_id"

    def get_queryset(self):
        return Perspective.objects.all()

    def get_object(self):
        return self.get_queryset().get(project_id=self.kwargs["project_id"])

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Perspective, PerspectiveQuestion, PerspectiveMember

class PerspectiveAnswerSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        perspective_id = request.data.get("perspective")
        answers = request.data.get("answers", [])

        try:
            perspective = Perspective.objects.get(id=perspective_id)
        except Perspective.DoesNotExist:
            return Response({"detail": "Perspetiva não encontrada."}, status=404)

        for item in answers:
            question_id = item.get("question_id")
            value = item.get("value", "").strip()

            if not question_id:
                continue

            try:
                question = PerspectiveQuestion.objects.get(id=question_id, perspective=perspective)
            except PerspectiveQuestion.DoesNotExist:
                continue

            # cria ou atualiza resposta
            member, created = PerspectiveMember.objects.update_or_create(
                perspective=perspective,
                user=user,
                question=question,
                defaults={"value": value}
            )

        return Response({"detail": "Respostas guardadas com sucesso."})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from labels.models import Category
from .models import Perspective, PerspectiveMember

class ProjectPerspectiveMemberDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            perspective = Perspective.objects.get(project_id=project_id)
        except Perspective.DoesNotExist:
            return Response({"detail": "Perspetiva não encontrada."}, status=404)

        members_data = []
        users_with_responses = PerspectiveMember.objects.filter(perspective=perspective).values_list("user", flat=True).distinct()

        for user_id in users_with_responses:
            user = User.objects.get(id=user_id)
            answers = PerspectiveMember.objects.filter(perspective=perspective, user=user).select_related("question__question")

            questions = [
                {
                    "question": a.question.question.question_text,
                    "answer": a.value
                }
                for a in answers
            ]

            labels = Category.objects.filter(example__project_id=project_id, user=user)

            members_data.append({
                "user": user.username,
                "user_id": user.id,
                "question_answers": questions,
                "labels": [l.label.text for l in labels]
            })

        return Response(members_data)

from rest_framework import status
from rest_framework.generics import DestroyAPIView
from .models import Perspective
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class DeleteProjectPerspectiveView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id):
        try:
            perspective = Perspective.objects.get(project_id=project_id)
            perspective.delete()  # isto apaga também as perguntas e membros associados (por cascade)
            return Response({"detail": "Perspetiva apagada com sucesso."}, status=status.HTTP_204_NO_CONTENT)
        except Perspective.DoesNotExist:
            return Response({"detail": "Perspetiva não encontrada."}, status=404)

class DeleteUserPerspectiveAnswersView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, user_id):
        try:
            perspective = Perspective.objects.get(project_id=project_id)
        except Perspective.DoesNotExist:
            return Response({"detail": "Perspetiva não encontrada."}, status=404)

        deleted, _ = PerspectiveMember.objects.filter(perspective=perspective, user_id=user_id).delete()
        return Response({"detail": f"{deleted} resposta(s) apagadas com sucesso."}, status=204)