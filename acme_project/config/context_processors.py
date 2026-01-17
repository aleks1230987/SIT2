from django.conf import settings

def site_settings(request):
    
    return {
        'SITE_NAME': 'Pantheon Project',
        'SITE_DESCRIPTION': 'Historical Popularity Index Database',
        'DEBUG': settings.DEBUG,
    }
