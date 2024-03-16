from django.conf import settings

media = f'{settings.SITE_DOMAIN}/media'

categories = [
    # {
    #     'title': ' Life Choices',
    #     'subtitle': 'Questions',
    #     'category': 'outdoor',
    #     'image_url': f'{media}/categories/tent.jpg'
    # },
    {
        'title': 'Normal',
        'subtitle': 'Questions',
        'category': 'normal',
        'image_url': f'{media}/categories/girl.jpg'
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
        'image_url': f'{media}/categories/why.jpg'
    },
    {
        'title': 'Fantasy',
        'subtitle': 'Questions',
        'category': 'fantasy',
        'image_url': f'{media}/categories/dragon.jpg'
    },
]

categories_list = ['normal', 'jobs', 'intriguing', 'fantasy']

categories_version = 'v1'
