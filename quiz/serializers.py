from rest_framework.serializers import ModelSerializer
from .models import User, Question, Answer, Mark, Category


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class QuestionSerializer(ModelSerializer):
    category_data = CategorySerializer(source='category', many=True)
    class Meta:
        model = Question
        exclude = ['category']


class AnswerSerializer(ModelSerializer):
    question_data = QuestionSerializer(source='question')
    class Meta:
        model = Answer
        exclude = ['question']


class MarkSerializer(ModelSerializer):
    answer_data = AnswerSerializer(source='answer')
    class Meta:
        model = Mark
        exclude = ['answer']
