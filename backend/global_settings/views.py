
# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view, renderer_classes
)
from rest_framework.renderers import JSONRenderer

from global_settings.languages import languages, languages_version
from global_settings.categories import categories, categories_version
from global_settings.app_info import current_api_version, current_app_version
from global_settings.questions import initial_questions


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def global_config(request):
    mobile_app_version = request.GET.get('version', '0.0.0')

    data = {
        # 'mobile_app_version': mobile_app_version,
        'update_required': mobile_app_version != current_app_version,
        'languages': languages,
        'languages_version': languages_version,
        'categories': categories,
        'categories_version': categories_version,
        'api_version': current_api_version,
        # 'app_version': current_app_version,
        'initial_questions': initial_questions,
    }

    return Response(data, status=status.HTTP_200_OK)
