from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from collections import defaultdict, Counter

from projects.models import Project
from examples.models import Example
from labels.models import Span, Category
from django.contrib.auth.models import User

from .models import Discrepancy
from .serializers import (
    DiscrepancySerializer,
    DiscrepancyCreateSerializer,
    DiscrepancyDetectSerializer
)

class DiscrepancyListCreateView(generics.ListCreateAPIView):
    serializer_class = DiscrepancySerializer

    def get_queryset(self):
        return Discrepancy.objects.filter(project_id=self.kwargs["project_id"])


class DiscrepancyDetectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        if project.project_type == "DocumentClassification":
            return self.handle_document_classification(project)
        elif project.project_type == "SequenceLabeling":
            return self.handle_sequence_labeling(project)
        else:
            return Response([])  # Tipo de projeto não suportado (ainda)

    def handle_document_classification(self, project):
        examples = Example.objects.filter(project=project)
        result = []

        for example in examples:
            labels = Category.objects.filter(example=example)
            label_counts = Counter()
            total_labels = 0

            for label in labels:
                label_counts[label.label.text] += 1
                total_labels += 1

            if len(label_counts) > 1:
                label_distribution = [
                    {
                        "label": label,
                        "count": count,
                        "percentage": (count / total_labels) * 100,
                    }
                    for label, count in label_counts.items()
                ]

                result.append({
                    "example_id": example.id,
                    "example_text": example.text,
                    "label_stats": label_distribution,
                    "type": "document_classification"
                })

        if not result:
            return Response(status=204)

        serializer = DiscrepancyDetectSerializer(result, many=True)
        return Response(serializer.data)

    def handle_sequence_labeling(self, project):
        examples = Example.objects.filter(project=project)
        result = []

        for example in examples:
            spans = Span.objects.filter(example=example)
            label_counts = Counter()
            total_labels = 0

            for span in spans:
                label_counts[span.label.text] += 1
                total_labels += 1

            if len(label_counts) > 1:
                label_distribution = [
                    {
                        "label": label,
                        "count": count,
                        "percentage": (count / total_labels) * 100,
                    }
                    for label, count in label_counts.items()
                ]

                result.append({
                    "example_id": example.id,
                    "example_text": example.text,
                    "label_stats": label_distribution,
                    "type": "sequence_labeling"
                })

        if not result:
            return Response(status=204)

        serializer = DiscrepancyDetectSerializer(result, many=True)
        return Response(serializer.data)


class DiscrepancySaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, example_id):
        data = request.data.copy()
        data["project"] = project_id
        data["example"] = example_id

        serializer = DiscrepancyCreateSerializer(data=data)
        if serializer.is_valid():
            discrepancy = serializer.save()
            return Response(DiscrepancyCreateSerializer(discrepancy).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiscrepancyUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discrepancy.objects.all()
    serializer_class = DiscrepancySerializer
    permission_classes = [IsAuthenticated]


class ExampleAnnotationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, example_id):
        try:
            example = Example.objects.get(id=example_id, project_id=project_id)
        except Example.DoesNotExist:
            return Response({"detail": "Example not found."}, status=404)

        result = {
            "example_id": example.id,
            "text": example.text,
            "annotations": []
        }

        category_annotations = Category.objects.filter(example=example)
        for annotation in category_annotations:
            result["annotations"].append({
                "user": annotation.user.username,
                "type": "Category",
                "label": annotation.label.text
            })

        span_annotations = Span.objects.filter(example=example)
        for annotation in span_annotations:
            result["annotations"].append({
                "user": annotation.user.username,
                "type": "Span",
                "label": annotation.label.text,
                "start_offset": annotation.start_offset,
                "end_offset": annotation.end_offset
            })

        return Response(result)
