# Python
import math
import re
import copy
import random
import traceback
from datetime import date
import uuid
from itertools import groupby
import os
import traceback


# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view, renderer_classes, permission_classes
)
from django.contrib.auth.hashers import make_password
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ValidationError
from django.db import transaction, IntegrityError
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q
from django.db.models import Case, When
from django.conf import settings


# Costume
from api.constants import AppMsg
from global_settings.categories import categories_list
from global_settings.languages import languages_list

# Models
from users.models import User
from api.models import (
    Question, UserProfile,
    QuestionType, Difficulty, Device,
    QuestionConfig,
)

from api.models import Status as StatusModel

# Serializers
from api.serializers import (
    QuestionModelSerializer,
    UserModelSerializer,
    UserProfileModelSerializer,
    DeviceModelSerializer,
    ScreenFlowSerializer,
)
from users.serializers import CustomTokenObtainPairSerializer

# Libraries
import uuid
import logging

logger = logging.getLogger('api_v1')
test_user_id = 1
appMsg = AppMsg()


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def user_data(request):
    try:
        user = UserProfile.objects.get(user=request.user.id)
        serializer = UserProfileModelSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as err:
        logger.error(traceback.format_exc())
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def user_sign_in(request):
    try:
        tokens = CustomTokenObtainPairSerializer(request.data).validate(
            request.data,
        )

        profile = UserProfile.objects.filter(
            email=request.data['email']).first()
        serializer = UserProfileModelSerializer(profile)

        return Response({
            'user': serializer.data,
            'refresh': str(tokens['refresh']),
            'access': str(tokens['access']),
        }, status=status.HTTP_200_OK)

    except AuthenticationFailed:
        return Response(appMsg.EMAIL_OR_PASS_INCORRECT, status=status.HTTP_401_UNAUTHORIZED)

    except:
        logger.error(traceback.format_exc())
        return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def user_sign_up(request):
    try:
        data = request.data.copy()

        found_user = User.objects.filter(email=data['email']).first()
        if found_user:
            return Response(appMsg.EMAIL_EXISTS, status=status.HTTP_409_CONFLICT)
        with transaction.atomic():
            user_serializer = UserModelSerializer(data={
                'email': data['email'],
                'password': make_password(
                    data['password'], salt=None, hasher='default'),
            })
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            profile_serializer = UserProfileModelSerializer(data={
                'email': data['email'],
                'user': user_serializer.data['id'],
                'english_level': data['english_level'],
                'verified': False,
                'screen_flow': True,
            })
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

            device_serializer = DeviceModelSerializer(data={
                'uuid': data['uuid'],
                'user': user_serializer.data['id']
            })
            device_serializer.is_valid(raise_exception=True)
            device_serializer.save()

        class UserPayload:
            id = user_serializer.data['id']

        refresh = CustomTokenObtainPairSerializer().get_token(UserPayload)

        return Response({
            'user': profile_serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    except Exception as err:
        logger.error(traceback.format_exc())
        return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def screen_flow(request):
    serializer = ScreenFlowSerializer(data={
        'device': request.data['device'],
        'value': request.data['value'],
        'time': request.data['time']
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response([], status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def device(request):
    if request.method == 'GET':
        uuid = request.GET.get('uuid', None)

        if not uuid:
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(uuid=uuid)
            return Response({'device_id': device.id}, status=status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        uuid = request.data.get('uuid', None)

        if not uuid:
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(uuid=uuid)
            if device:
                return Response({
                    'message': 'Device already exists.'
                }, status=status.HTTP_409_CONFLICT)
        except:
            pass

        serializer = DeviceModelSerializer(data={
            'uuid': uuid,
        })

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'device_id': serializer.data['id']}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def categories_list_view(request):
    media = f'{settings.SITE_DOMAIN}/media'

    return Response([
        {
            'title': 'Outdoor',
            'subtitle': 'Questions',
            'category': 'outdoor',
            'image_url': f'{media}/categories/tent.png'
        },
        {
            'title': 'Normal',
            'subtitle': 'Questions',
            'category': 'normal',
            'image_url': f'{media}/categories/girl.png'
        },
        {
            'title': 'Job Interview',
            'subtitle': 'Questions',
            'category': 'jobs',
            'image_url': f'{media}/categories/job.jpg'
        },
        {
            'title': 'Why & How',
            'subtitle': 'Questions',
            'category': 'intriguing',
            'image_url': f'{media}/categories/why.png'
        },
        {
            'title': 'Fantasy',
            'subtitle': 'Questions',
            'category': 'fantasy',
            'image_url': f'{media}/categories/dragon.png'
        },
    ])


def get_random_question(category, excluded_ids):
    questions = Question.objects.filter(
        category=category,
        ranking=3,
        status=StatusModel.ACTIVE,
        # example__isnull=False
    ).exclude(id__in=excluded_ids)
    return random.choice(questions)


def get_question_by_code(question_code):
    return Question.objects.filter(
        code=question_code
    ).first()


@api_view(['GET'])
def questions_list_view(request):
    try:
        round_number = request.GET.get('round', None)
        language = request.GET.get('lang', None)
        category = request.GET.get('category', None)
        codes = request.GET.get('codes', None)

        if not round_number:
            return Response([])

        if category not in categories_list:
            return Response([])

        if language not in languages_list:
            return Response([])

        questions = []

        if codes:
            codes_list = codes.split(',')
            for code in codes_list:
                if len(questions) >= 3:
                    break
                q = get_question_by_code(code)
                questions.append(q)

            questions_left = 3 - len(questions)

            for _ in range(questions_left):
                excluded_ids = [
                    question.id for question in questions if question]
                q = get_random_question(category, excluded_ids)
                questions.append(q)
        else:
            questions_left = 3
            for _ in range(questions_left):
                excluded_ids = [
                    question.id for question in questions if question]
                q = get_random_question(category, excluded_ids)
                questions.append(q)

        result = []
        media = settings.SITE_DOMAIN + '/media'

        if category == 'normal':
            normal_imgs = [
                'shared/imgs/normal01.webp',
                'shared/imgs/normal02.webp',
                'shared/imgs/normal03.webp',
                'shared/imgs/normal04.webp',
                'shared/imgs/normal05.webp',
            ]

            img_url = f'{media}/{random.choice(normal_imgs)}'

            for q in questions:
                result.append({
                    'id': q.id,
                    'question': q.question,
                    'translation': q.translations[language],
                    'type': q.type,
                    'code': q.code,
                    'image_url': q.image_url if q.image_url else img_url,
                    'voice_url': q.voice_url,
                    'example': q.example,
                    'scenario': q.scenario,
                    'style': q.style
                })
        elif category == 'jobs':
            job_imgs = [
                'shared/imgs/job01.webp',
                'shared/imgs/job02.webp',
                'shared/imgs/job03.webp',
                'shared/imgs/job04.webp',
                'shared/imgs/job05.webp',
            ]

            img_url = f'{media}/{random.choice(job_imgs)}'

            for q in questions:
                result.append({
                    'id': q.id,
                    'question': q.question,
                    'translation': q.translations[language],
                    'type': q.type,
                    'code': q.code,
                    'image_url': q.image_url if q.image_url else img_url,
                    'voice_url': q.voice_url,
                    'example': q.example,
                    'scenario': q.scenario,
                    'style': q.style
                })
        else:
            for q in questions:
                logger.debug(q)
                result.append({
                    'id': q.id,
                    'question': q.question,
                    'translation': q.translations[language],
                    'type': q.type,
                    'code': q.code,
                    'image_url': q.image_url,
                    'voice_url': q.voice_url,
                    'example': q.example,
                    'scenario': q.scenario,
                    'style': q.style
                })

        return Response(result)

    except Exception as err:
        logger.error(err)
        stacktrace = traceback.format_exc()
        logger.error("Stacktrace:\n%s", stacktrace)
        return Response([])


@api_view(['GET'])
def set_questions_config(request):
    ids = request.GET.get('ids', None)
    questions_type = request.GET.get('questions_type', None)
    questions_search = request.GET.get('questions_search', None)

    question_config = QuestionConfig.objects.get()

    if ids is not None:
        question_config.ids = ids
    if questions_type is not None:
        question_config.questions_type = questions_type
    if questions_search is not None:
        question_config.questions_search = questions_search

    question_config.save()

    return Response('Coool!', status=status.HTTP_200_OK)


@api_view(['GET'])
def hola(request):

    # DEBUG = os.getenv('DEBUG', False) == 'False'
    return Response({'DEBUG': 'DEBUG'}, status=status.HTTP_200_OK)
