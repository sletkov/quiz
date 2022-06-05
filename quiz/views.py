from rest_framework.exceptions import AuthenticationFailed, ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
import django_filters.rest_framework
from django.db.models import Q
from .models import Answer, Category, Mark, Question, User
from .serializers import AnswerSerializer, CategorySerializer, MarkSerializer, QuestionSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data['password']
        if len(password) < 8:
            raise ValidationError({'password': 'Password is too short'})

        user = User.objects.create(
            email=serializer.validated_data['email'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            )
        user.is_active = True
        user.set_password(password)
        user.save()

        return Response({'message': 'success'}, status=HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def login(self, request):
        if 'email' not in request.data:
            data = {'email': 'Email must be provided'}
            raise ValidationError(data)
        if 'password' not in request.data:
            data = {'password': 'Password must be provided'}
            raise ValidationError(data)

        try:
            user = User.objects.get(email=request.data.get('email'))
        except User.DoesNotExist:
            raise NotFound({'message': 'User with provided credentials does not exist'})

        if not user.check_password(request.data.get('password')):
            raise AuthenticationFailed({'message': 'Incorrect password'})

        refresh = RefreshToken.for_user(user)
        response = Response()
        response.set_cookie('refresh', str(refresh))
        response.data = {'access': str(refresh.access_token)}
        return response

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def user(self, request):
        user = request.user
        data = UserSerializer(user).data
        return Response(data)

    @action(detail=True, methods=['POST'], url_path='set_password')
    def set_password(self, request, pk=None):
        if 'new_password' not in request.data:
            raise ValidationError({'password': 'Password must be provided'})

        password = request.data['new_password']
        user = self.get_object()
        user.set_password(password)
        user.save()
        return Response({'status': 'password set'})


class AdminOrStaffViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True))


class QuestionViewSet(ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


class AnswerViewSet(ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()


class MarkViewSet(ModelViewSet):
    serializer_class = MarkSerializer
    queryset = Mark.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['mark', 'answer__text', 'answer__question']


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
