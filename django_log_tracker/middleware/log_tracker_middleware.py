import requests
import json
import time
from django.conf import settings
from django.urls import resolve
from django.utils import timezone

from django_log_tracker import LOG_TRACKER_SIGNAL
from django_log_tracker.start_logger_when_server_starts import LOGGER_THREAD
from django_log_tracker.utils import get_headers, get_client_ip, get_client_ip_geolocation, mask_sensitive_data, \
    is_get_client_ip_enabled

"""
File: log_tracker_middleware.py
Class: LogTrackerMiddleware
"""


class LogTrackerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

        self.DJANGO_LOG_TRACKER_DATABASE = False
        if hasattr(settings, 'DJANGO_LOG_TRACKER_DATABASE'):
            self.DJANGO_LOG_TRACKER_DATABASE = settings.DJANGO_LOG_TRACKER_DATABASE

        self.DJANGO_LOG_TRACKER_SIGNAL = False
        if hasattr(settings, 'DJANGO_LOG_TRACKER_SIGNAL'):
            self.DJANGO_LOG_TRACKER_SIGNAL = settings.DJANGO_LOG_TRACKER_SIGNAL

        self.DJANGO_LOG_TRACKER_PATH_TYPE = 'ABSOLUTE'
        if hasattr(settings, 'DJANGO_LOG_TRACKER_PATH_TYPE'):
            if settings.DJANGO_LOG_TRACKER_PATH_TYPE in ['ABSOLUTE', 'RAW_URI', 'FULL_PATH']:
                self.DJANGO_LOG_TRACKER_PATH_TYPE = settings.DJANGO_LOG_TRACKER_PATH_TYPE

        self.DJANGO_LOG_TRACKER_SKIP_URL_NAME = []
        if hasattr(settings, 'DJANGO_LOG_TRACKER_SKIP_URL_NAME'):
            if type(settings.DJANGO_LOG_TRACKER_SKIP_URL_NAME) is tuple or type(
                    settings.DJANGO_LOG_TRACKER_SKIP_URL_NAME) is list:
                self.DJANGO_LOG_TRACKER_SKIP_URL_NAME = settings.DJANGO_LOG_TRACKER_SKIP_URL_NAME

        self.DJANGO_LOG_TRACKER_SKIP_NAMESPACE = []
        if hasattr(settings, 'DJANGO_LOG_TRACKER_SKIP_NAMESPACE'):
            if type(settings.DJANGO_LOG_TRACKER_SKIP_NAMESPACE) is tuple or type(
                    settings.DJANGO_LOG_TRACKER_SKIP_NAMESPACE) is list:
                self.DJANGO_LOG_TRACKER_SKIP_NAMESPACE = settings.DJANGO_LOG_TRACKER_SKIP_NAMESPACE

        self.DJANGO_LOG_TRACKER_METHODS = []
        if hasattr(settings, 'DJANGO_LOG_TRACKER_METHODS'):
            if type(settings.DJANGO_LOG_TRACKER_METHODS) is tuple or type(
                    settings.DJANGO_LOG_TRACKER_METHODS) is list:
                self.DJANGO_LOG_TRACKER_METHODS = settings.DJANGO_LOG_TRACKER_METHODS

        self.DJANGO_LOG_TRACKER_IP = False
        if hasattr(settings, 'DJANGO_LOG_TRACKER_IP'):
            self.DJANGO_LOG_TRACKER_IP = settings.DJANGO_LOG_TRACKER_IP

        self.DJANGO_LOG_TRACKER_IP_GEOLOCATION = False
        if hasattr(settings, 'DJANGO_LOG_TRACKER_IP_GEOLOCATION'):
            self.DJANGO_LOG_TRACKER_IP_GEOLOCATION = settings.DJANGO_LOG_TRACKER_IP_GEOLOCATION

    def __call__(self, request):

        # Run only if logger is enabled.
        if self.DJANGO_LOG_TRACKER_DATABASE or self.DJANGO_LOG_TRACKER_SIGNAL:

            url_name = resolve(request.path).url_name
            namespace = resolve(request.path).namespace

            # Always skip Admin panel
            if namespace == 'admin':
                return self.get_response(request)

            # Skip for url name
            if url_name in self.DJANGO_LOG_TRACKER_SKIP_URL_NAME:
                return self.get_response(request)

            # Skip entire app using namespace
            if namespace in self.DJANGO_LOG_TRACKER_SKIP_NAMESPACE:
                return self.get_response(request)

            start_time = time.time()
            request_data = ''
            try:
                request_data = json.loads(request.body) if request.body else ''
            except:
                pass

            # Code to be executed for each request before
            # the view (and later middleware) are called.
            response = self.get_response(request)

            # Code to be executed for each request/response after
            # the view is called.

            headers = get_headers(request=request)
            method = request.method

            # Log only registered methods if available.
            if len(self.DJANGO_LOG_TRACKER_METHODS) > 0 and method not in self.DJANGO_LOG_TRACKER_METHODS:
                return self.get_response(request)

            if response.get('content-type') in ('application/json', 'application/vnd.api+json',):
                if getattr(response, 'streaming', False):
                    response_body = '** Streaming **'
                else:
                    if type(response.content) == bytes:
                        response_body = json.loads(response.content.decode())
                    else:
                        response_body = json.loads(response.content)
                if self.DJANGO_LOG_TRACKER_PATH_TYPE == 'ABSOLUTE':
                    api = request.build_absolute_uri()
                elif self.DJANGO_LOG_TRACKER_PATH_TYPE == 'FULL_PATH':
                    api = request.get_full_path()
                elif self.DJANGO_LOG_TRACKER_PATH_TYPE == 'RAW_URI':
                    api = request.get_raw_uri()
                else:
                    api = request.build_absolute_uri()

                if self.DJANGO_LOG_TRACKER_IP:
                    client_ip_address = get_client_ip()
                else:
                    client_ip_address = ''

                if self.DJANGO_LOG_TRACKER_IP_GEOLOCATION:
                    client_ip_geolocation = get_client_ip_geolocation()
                else:
                    client_ip_geolocation = ''

                data = dict(
                    api=api,
                    status=requests.status_codes._codes[200][0],
                    headers=mask_sensitive_data(headers),
                    method=method,
                    client_ip_address=client_ip_address,
                    client_ip_geolocation=client_ip_geolocation,
                    response=mask_sensitive_data(response_body),
                    status_code=response.status_code,
                    execution_time=time.time() - start_time,
                    user_agent=request.META['HTTP_USER_AGENT'],
                    added_on=timezone.now()
                )
                if self.DJANGO_LOG_TRACKER_DATABASE:
                    if LOGGER_THREAD:
                        d = data.copy()
                        d['headers'] = json.dumps(d['headers'], indent=4)
                        if request_data:
                            d['body'] = json.dumps(d['body'], indent=4)
                        d['response'] = json.dumps(d['response'], indent=4)
                        LOGGER_THREAD.put_log_data(data=d)
                if self.DJANGO_LOG_TRACKER_SIGNAL:
                    LOG_TRACKER_SIGNAL.listen(**data)
            else:
                return response
        else:
            response = self.get_response(request)
        return response
