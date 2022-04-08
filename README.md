# django_log_tracker: A Django app to conduct api logs
![version](https://img.shields.io/badge/version-1.0.2-blue.svg)
[![Open Source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/)

<a href="https://github.com/Ragib01/django_log_tracker"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/></a>

It logs all the API information for content type "application/json".

## Database fields:

- status
- api
- method
- headers
- client_ip_address
- client_ip_geolocation
- response
- status_code
- execution_time
- user_agent
- added_on

## Installation

1. PyPI

```sh
pip install django-log-tracker
```

2. Install requests

```shell
pip install requests
```

3. Add "django_log_tracker" to your INSTALLED_APPS setting like this

```python
INSTALLED_APPS = [
    ...,
    'django_log_tracker',
]
```

4. Add in MIDDLEWARE

```python
MIDDLEWARE = [
    ...,
    'django_log_tracker.middleware.log_tracker_middleware.LogTrackerMiddleware',
]
```

5. Run

```shell
python manage.py migrate
```

####  Add these lines in settings file.


### Store logs into the database

Log every request into the database.

```python
DJANGO_LOG_TRACKER_DATABASE = True  # Default to False
```

- Logs will be available in Django Admin Panel.

![logs](https://github.com/Ragib01/django_log_tracker/blob/main/logs.png?raw=true)

- The search bar will search in Request Body, Response, Headers and API URL.

![search-bar](https://github.com/Ragib01/django_log_tracker/blob/main/search-bar.png?raw=true)

- You can also filter the logs based on the "added_on" date, Status Code and Request Methods.

![filter-box](https://github.com/Ragib01/django_log_tracker/blob/main/filter-box.png?raw=true)

### Track client ip address

![ip](https://github.com/Ragib01/django_log_tracker/blob/main/ip.png?raw=true)

```python
DJANGO_LOG_TRACKER_IP = True # Default to False
```

### Track client ip geolocation

```python
DJANGO_LOG_TRACKER_IP_GEOLOCATION = True # Default to False
```

#### Note:
> API response may get slower for ***DJANGO_LOG_TRACKER_IP*** and
***DJANGO_LOG_TRACKER_IP_GEOLOCATION***. So by default they both are false.

### API Data into Charts

![chart](https://github.com/Ragib01/django_log_tracker/blob/main/graph.png?raw=true)

#### Check version
```shell
>>> import django_log_tracker
>>> django_log_tracker.__version__
```

