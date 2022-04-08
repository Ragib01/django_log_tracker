import re
import requests
from django.conf import settings
import json
from urllib.request import urlopen

SENSITIVE_KEYS = ['password', 'token', 'access', 'refresh']
if hasattr(settings, 'DJANGO_LOG_TRACKER_EXCLUDE_KEYS'):
    if type(settings.DJANGO_LOG_TRACKER_EXCLUDE_KEYS) in (list, tuple):
        SENSITIVE_KEYS.extend(settings.DJANGO_LOG_TRACKER_EXCLUDE_KEYS)


def get_headers(request=None):
    """
        Function:       get_headers(self, request)
        Description:    To get all the headers from request
    """
    regex = re.compile('^HTTP_')
    return dict((regex.sub('', header), value) for (header, value)
                in request.META.items() if header.startswith('HTTP_'))


def get_client_ip():
    try:
        url = 'http://ipinfo.io/json'
        response = urlopen(url)
        data = json.load(response)

        ip = data['ip']
        return ip
    except:
        return ''


def get_client_ip_geolocation():
    try:
        url = 'http://ipinfo.io/json'
        response = urlopen(url)
        data = json.load(response)
        ip = data['ip']

        geo = requests.get(f'http://ip-api.com/json/{ip}').json()
        return geo
    except:
        return ''


def is_django_log_tracker_enabled():
    django_log_tracker_database = False
    if hasattr(settings, 'DJANGO_LOG_TRACKER_DATABASE'):
        django_log_tracker_database = settings.DJANGO_LOG_TRACKER_DATABASE

    django_log_tracker_signal = False
    if hasattr(settings, 'DJANGO_LOG_TRACKER_SIGNAL'):
        django_log_tracker_signal = settings.DJANGO_LOG_TRACKER_SIGNAL
    return django_log_tracker_database or django_log_tracker_signal


def database_log_enabled():
    django_log_tracker_database = True
    if hasattr(settings, 'DJANGO_LOG_TRACKER_DATABASE'):
        django_log_tracker_database = settings.DJANGO_LOG_TRACKER_DATABASE
    return django_log_tracker_database


def mask_sensitive_data(data):
    """
    Hides sensitive keys specified in sensitive_keys settings.
    Loops recursively over nested dictionaries.
    """

    if type(data) != dict:
        return data

    for key, value in data.items():
        if key in SENSITIVE_KEYS:
            data[key] = "***FILTERED***"

        if type(value) == dict:
            data[key] = mask_sensitive_data(data[key])

        if type(value) == list:
            data[key] = [mask_sensitive_data(item) for item in data[key]]

    return data


def is_get_client_ip_enabled():
    django_log_tracker_ip = False
    if hasattr(settings, 'DJANGO_LOG_TRACKER_IP'):
        django_log_tracker_ip = settings.DJANGO_LOG_TRACKER_IP
    return django_log_tracker_ip
