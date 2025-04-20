from rest_framework import serializers
from .models import (
    Perspective,
    PerspectiveQuestionBase,
    PerspectiveQuestion,
    PerspectiveMember
)


class PerspectiveQuestionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveQuestionBase
        fields = ["id", "question_text"]


class PerspectiveQuestionSerializer(serializers.ModelSerializer):
    question = PerspectiveQuestionBaseSerializer()

    class Meta:
        model = PerspectiveQuestion
        fields = ["id", "question"]


class PerspectiveSerializer(serializers.ModelSerializer):
    questions = PerspectiveQuestionSerializer(many=True)

    class Meta:
        model = Perspective
        fields = ["id", "project", "questions"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        perspective = Perspective.objects.create(**validated_data)
        for question_data in questions_data:
            base_data = question_data["question"]
            base_question, _ = PerspectiveQuestionBase.objects.get_or_create(
                question_text=base_data["question_text"]
            )
            PerspectiveQuestion.objects.create(
                perspective=perspective, question=base_question
            )
        return perspective
