from django.conf import settings

media = f'{settings.SITE_DOMAIN}/media'

languages = [
    {
        'code': 'arabic',
        'name': 'Arabic',
        'image_url': f'{media}/flags/arabic_round.png'
    },
    {
        'code': 'bengali',
        'name': 'Bengali',
        'image_url': f'{media}/flags/bengali_round.png'
    },
    {
        'code': 'chinese',
        'name': 'Chinese',
        'image_url': f'{media}/flags/chinese_round.png'
    },
    {
        'code': 'hindi',
        'name': 'Hindi',
        'image_url': f'{media}/flags/hindi_round.png'
    },
    {
        'code': 'indonesian',
        'name': 'Indonesian',
        'image_url': f'{media}/flags/indonesian_round.png'
    },
    {
        'code': 'portuguese',
        'name': 'Portuguese',
        'image_url': f'{media}/flags/portuguese_round.png'
    },
    {
        'code': 'turkish',
        'name': 'Turkish',
        'image_url': f'{media}/flags/turkish_round.png'
    },
    {
        'code': 'spanish',
        'name': 'Spanish',
        'image_url': f'{media}/flags/spanish_round.png'
    },
    {
        'code': 'vietnamese',
        'name': 'Vietnamese',
        'image_url': f'{media}/flags/vietnamese_round.png'
    },
]


languages_list = ['spanish', 'portuguese', 'chinese', 'arabic',
             'hindi', 'turkish', 'indonesian', 'vietnamese', 'bengali']

languages_version = 'v1'
