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


# Data
from api.constants import AppMsg

# Models
from users.models import User
from api.models import (
    Question, UserProfile, Style,
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
    StylePresentationSerializer,
    ScreenFlowSerializer,
)
from users.serializers import CustomTokenObtainPairSerializer

# Libraries
import uuid
import logging

logger = logging.getLogger('api_v1')
test_user_id = 1
appMsg = AppMsg()


langues = ['es', 'zh-Hans', 'pt', 'ar', 'hi']


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


def scenario_questions(config):
    if config.questions_search == 'random':
        questions = Question.objects.filter(
            type=QuestionType.SCENARIO,
            status=StatusModel.ACTIVE
        )
        return [random.choice(questions)]

    if config.questions_search == 'hardcoded':
        ids = config.hardcoded_ids.split(',')

        questions = Question.objects.filter(
            id__in=[int(x) for x in ids]
        )
        return [random.choice(questions)]


def normal_questions(config):
    if config.questions_search == 'random':
        easy_questions = Question.objects.filter(
            type=QuestionType.DESCRIBE,
            status=StatusModel.ACTIVE
        )
        easy_question = random.choice(easy_questions)

        quiz_questions = Question.objects.filter(
            status=StatusModel.ACTIVE
        ).exclude(type__in=[QuestionType.DESCRIBE, QuestionType.SCENARIO])
        quiz_question = random.choice(quiz_questions)

        ids = [easy_question.id, quiz_question.id]
        whatever_questions = list(Question.objects.filter(status=StatusModel.ACTIVE).exclude(
            id__in=ids).exclude(type=QuestionType.SCENARIO))
        questions = [easy_question, quiz_question,
                     random.choice(whatever_questions)]

        return questions

    if config.questions_search == 'hardcoded':
        ids = config.hardcoded_ids.split(',')
        ids = [int(x) for x in ids]
        preserved = Case(*[When(id=id, then=pos)
                         for pos, id in enumerate(ids)])
        questions = Question.objects.filter(id__in=ids).order_by(preserved)
        return questions


def random_questions(config):
    if random.random() < 0.35:
        return scenario_questions(config)
    else:
        return normal_questions(config)


def first_time_questions(viewed_pack_ids, starting_question_packs):

    pack_ids = list(map(lambda p: p['id'], starting_question_packs))

    question_ids = []

    for pack_id in pack_ids:
        if pack_id not in viewed_pack_ids:
            found_pack = list(
                filter(lambda x: x['id'] == pack_id, starting_question_packs))
            question_ids = found_pack[0]['question_ids']
            break

    if len(question_ids) > 0:
        preserved = Case(*[When(id=id, then=pos)
                         for pos, id in enumerate(question_ids)])
        questions = Question.objects.filter(
            id__in=question_ids).order_by(preserved)
        return questions
    return []


@api_view(['GET'])
def questions(request):

    lang = request.GET.get('lang', None)
    # first_time = request.GET.get('first_time', None)
    # ids = [int(id) for id in request.GET.get('ids', '').split(',') if id]
    first_time = '2'
    ids = [1, 2, 3, 4, 5]

    config = QuestionConfig.objects.all().first()

    if first_time == '1':
        questions = first_time_questions(ids, config.starting_questions)

    else:
        if config.questions_type == 'random':
            questions = random_questions(config)

        if config.questions_type == 'normal':
            questions = normal_questions(config)

        if config.questions_type == 'scenario':
            questions = scenario_questions(config)

    result = []
    for q in questions:
        style = Style.objects.get(question=q.id)

        result.append({
            'id': q.id,
            'question': q.question,
            'type': q.type,
            'image_url': q.image_url,
            'voice_url': q.voice_url,
            'example': q.example,
            'scenario': q.scenario,
            'style': StylePresentationSerializer(style).data
        })

    return Response(result)


def get_translation(items, lang):
    lang = 'es' if lang is None else lang
    result = ''
    for item in items:
        if item['lang'] == lang:
            result = item['text']
    return result


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