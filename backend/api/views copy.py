# # Python
# import math
# import re
# import copy
# import random
# import traceback
# from datetime import date
# import uuid
# from itertools import groupby
# import os

# # Framework
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import (
#     api_view, renderer_classes, permission_classes
# )
# from django.contrib.auth.hashers import make_password
# from rest_framework.renderers import JSONRenderer
# from rest_framework.serializers import ValidationError
# from django.db import transaction, IntegrityError
# from rest_framework.exceptions import AuthenticationFailed
# from django.db.models import Q
# from django.db.models import Case, When


# # Data
# from api.constants import AppMsg

# # Models
# from users.models import User
# from api.models import (
#     Word, Question, UserProfile, Style,
#     QuestionType, Difficulty, Device,
#     QuestionConfig,
# )

# from api.models import Status as StatusModel

# # Serializers
# from api.serializers import (
#     QuestionModelSerializer,
#     UserModelSerializer,
#     UserProfileModelSerializer,
#     DeviceModelSerializer,
#     WordModelSerializer,
#     StylePresentationSerializer,
#     ScreenFlowSerializer,
# )
# from users.serializers import CustomTokenObtainPairSerializer

# # Libraries
# import uuid
# from textblob import TextBlob
# import nltk
# from nltk.corpus import wordnet as wn
# from word_forms.word_forms import get_word_forms
# import logging
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer
# import inflect
# from nltk.stem.snowball import SnowballStemmer


# logger = logging.getLogger('api_v1')
# test_user_id = 1
# appMsg = AppMsg()


# langues = ['es', 'zh-Hans', 'pt', 'ar', 'hi']


# @api_view(['GET'])
# @renderer_classes([JSONRenderer])
# @permission_classes([IsAuthenticated])
# def user_data(request):
#     try:
#         user = UserProfile.objects.get(user=request.user.id)
#         serializer = UserProfileModelSerializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     except Exception as err:
#         logger.error(traceback.format_exc())
#         return Response({}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @renderer_classes([JSONRenderer])
# def user_sign_in(request):
#     try:
#         tokens = CustomTokenObtainPairSerializer(request.data).validate(
#             request.data,
#         )

#         profile = UserProfile.objects.filter(
#             email=request.data['email']).first()
#         serializer = UserProfileModelSerializer(profile)

#         return Response({
#             'user': serializer.data,
#             'refresh': str(tokens['refresh']),
#             'access': str(tokens['access']),
#         }, status=status.HTTP_200_OK)

#     except AuthenticationFailed:
#         return Response(appMsg.EMAIL_OR_PASS_INCORRECT, status=status.HTTP_401_UNAUTHORIZED)

#     except:
#         logger.error(traceback.format_exc())
#         return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @renderer_classes([JSONRenderer])
# def user_sign_up(request):
#     try:
#         data = request.data.copy()

#         found_user = User.objects.filter(email=data['email']).first()
#         if found_user:
#             return Response(appMsg.EMAIL_EXISTS, status=status.HTTP_409_CONFLICT)
#         with transaction.atomic():
#             user_serializer = UserModelSerializer(data={
#                 'email': data['email'],
#                 'password': make_password(
#                     data['password'], salt=None, hasher='default'),
#             })
#             user_serializer.is_valid(raise_exception=True)
#             user_serializer.save()

#             profile_serializer = UserProfileModelSerializer(data={
#                 'email': data['email'],
#                 'user': user_serializer.data['id'],
#                 'english_level': data['english_level'],
#                 'verified': False,
#                 'screen_flow': True,
#             })
#             profile_serializer.is_valid(raise_exception=True)
#             profile_serializer.save()

#             device_serializer = DeviceModelSerializer(data={
#                 'uuid': data['uuid'],
#                 'user': user_serializer.data['id']
#             })
#             device_serializer.is_valid(raise_exception=True)
#             device_serializer.save()

#         class UserPayload:
#             id = user_serializer.data['id']

#         refresh = CustomTokenObtainPairSerializer().get_token(UserPayload)

#         return Response({
#             'user': profile_serializer.data,
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }, status=status.HTTP_201_CREATED)

#     except Exception as err:
#         logger.error(traceback.format_exc())
#         return Response(appMsg.UNKNOWN_ERROR, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def hola(request):

#     DEBUG = os.getenv('DEBUG', False) == 'False'
#     return Response({'DEBUG': DEBUG}, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def screen_flow(request):
#     serializer = ScreenFlowSerializer(data={
#         'device': request.data['device'],
#         'value': request.data['value'],
#         'time': request.data['time']
#     })
#     serializer.is_valid(raise_exception=True)
#     serializer.save()

#     return Response([], status=status.HTTP_201_CREATED)


# @api_view(['GET', 'POST'])
# def device(request):
#     if request.method == 'GET':
#         uuid = request.GET.get('uuid', None)

#         if not uuid:
#             return Response([], status=status.HTTP_400_BAD_REQUEST)

#         try:
#             device = Device.objects.get(uuid=uuid)
#             return Response({'device_id': device.id}, status=status.HTTP_200_OK)
#         except:
#             return Response({}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'POST':
#         uuid = request.data.get('uuid', None)

#         if not uuid:
#             return Response([], status=status.HTTP_400_BAD_REQUEST)

#         try:
#             device = Device.objects.get(uuid=uuid)
#             if device:
#                 return Response({
#                     'message': 'Device already exists.'
#                 }, status=status.HTTP_409_CONFLICT)
#         except:
#             pass

#         serializer = DeviceModelSerializer(data={
#             'uuid': uuid,
#         })

#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({'device_id': serializer.data['id']}, status=status.HTTP_201_CREATED)


# def scenario_questions(first_time, config):
#     if config.questions_search == 'random':
#         questions = Question.objects.filter(
#             type=QuestionType.SCENARIO,
#             status=StatusModel.ACTIVE
#         )
#         return [random.choice(questions)]

#     if config.questions_search == 'hardcoded':
#         ids = config.ids.split(',')

#         questions = Question.objects.filter(
#             id__in=[int(x) for x in ids]
#         )
#         return [random.choice(questions)]


# def normal_questions(first_time, config):
#     if first_time:
#         preserved = Case(*[When(pk=pk, then=pos)
#                          for pos, pk in enumerate(pk_list)])
#         questions = Question.objects.filter(pk__in=pk_list).order_by(preserved)
#         return questions

#     if config.questions_search == 'random':
#         # pk_list = [39, 12, 24, 30]
#         # pk_list = [40, 42, 43, 44, 45]
#         pk_list = [39, 37, 24, 30]
#         # easy_questions = Question.objects.filter(
#         #     type=QuestionType.DESCRIBE,
#         #     difficulty=Difficulty.EASY,
#         #     status=StatusModel.ACTIVE
#         # )
#         easy_questions = Question.objects.filter(
#             type=QuestionType.DESCRIBE,
#             status=StatusModel.ACTIVE
#         ).exclude(id__in=pk_list)
#         easy_question = random.choice(easy_questions)

#         quiz_questions = Question.objects.filter(
#             status=StatusModel.ACTIVE
#         ).exclude(type__in=[QuestionType.DESCRIBE, QuestionType.SCENARIO]).exclude(id__in=pk_list)
#         quiz_question = random.choice(quiz_questions)

#         ids = pk_list + [easy_question.id, quiz_question.id]
#         whatever_questions = list(Question.objects.filter(status=StatusModel.ACTIVE).exclude(
#             id__in=ids).exclude(type=QuestionType.SCENARIO))
#         questions = [easy_question, quiz_question, random.choice(whatever_questions)]
#         # questions = random.sample(questions, 1)
#         # questions.insert(0, easy_question)
#         # questions.insert(1, quiz_question)

#         return questions

#     if config.questions_search == 'hardcoded':
#         ids = config.ids.split(',')
#         ids = [int(x) for x in ids]
#         preserved = Case(*[When(id=id, then=pos)
#                          for pos, id in enumerate(ids)])
#         questions = Question.objects.filter(id__in=ids).order_by(preserved)
#         return questions


# def random_questions(first_time, config):
#     if random.random() < 0.35:
#         return scenario_questions(first_time, config)
#     else:
#         return normal_questions(first_time, config)
    
# def first_time_questions(first_time, config):
#     if random.random() < 0.35:
#         return scenario_questions(first_time, config)
#     else:
#         return normal_questions(first_time, config)


# @api_view(['GET'])
# def questions(request):

#     # first_time = request.GET.get('first_time', None)
#     first_time = False

#     config = QuestionConfig.objects.all().first()

#     if config.questions_type == 'first-time':
#         questions = first_time_questions(first_time, config)

#     if config.questions_type == 'random':
#         questions = random_questions(first_time, config)

#     if config.questions_type == 'normal':
#         questions = normal_questions(first_time, config)

#     if config.questions_type == 'scenario':
#         questions = scenario_questions(first_time, config)

#     lang = request.GET.get('lang', None)

#     result = []
#     for q in questions:
#         words = []
#         for w in q.words.filter(status=StatusModel.ACTIVE):
#             examples = []
#             for ex in w.examples:
#                 examples.append({
#                     'value': ex['value'],
#                     'voice_url': ex['voice_url'],
#                     'translation': get_translation(ex['translations'], lang),
#                 })

#             explanations = [{
#                 'image': w.explanations[0]['image'],
#                 'value': w.explanations[0]['value'],
#                 'translation': get_translation(w.explanations[0]['translations'], lang),
#             }]

#             words.append({
#                 'id': w.id,
#                 'word': w.word,
#                 'definition': w.definition,
#                 'translation': get_translation(w.translations, lang),
#                 'has_info': w.has_info,
#                 'examples': examples,
#                 'explanations': explanations,
#                 'story': w.story,
#                 'miniature': w.miniature
#             })

#         style = Style.objects.get(question=q.id)

#         result.append({
#             'id': q.id,
#             'question': q.question,
#             'type': q.type,
#             'image_url': q.image_url,
#             'voice_url': q.voice_url,
#             'example': q.example,
#             'scenario': q.scenario,
#             'words': words,
#             'style': StylePresentationSerializer(style).data
#         })

#     return Response(result)


# def get_translation(items, lang):
#     lang = 'es' if lang is None else lang
#     result = ''
#     for item in items:
#         if item['lang'] == lang:
#             result = item['text']
#     return result


# @api_view(['GET'])
# def set_questions_config(request):
#     ids = request.GET.get('ids', None)
#     questions_type = request.GET.get('questions_type', None)
#     questions_search = request.GET.get('questions_search', None)

#     question_config = QuestionConfig.objects.get()

#     if ids is not None:
#         question_config.ids = ids
#     if questions_type is not None:
#         question_config.questions_type = questions_type
#     if questions_search is not None:
#         question_config.questions_search = questions_search

#     question_config.save()

#     return Response('Coool!', status=status.HTTP_200_OK)
