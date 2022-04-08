from datetime import timedelta

from django.conf import settings
from django.contrib import admin
from django.db.models import Count
from .utils import database_log_enabled
from .models import LogTracker

if database_log_enabled():

    from django.utils.translation import gettext_lazy as _


    class SlowAPIsFilter(admin.SimpleListFilter):
        title = _('API Performance')

        # Parameter for the filter that will be used in the URL query.
        parameter_name = 'api_performance'

        def __init__(self, request, params, model, model_admin):
            super().__init__(request, params, model, model_admin)
            if hasattr(settings, 'DJANGO_LOG_TRACKER_SLOW_API_ABOVE'):
                if type(settings.DJANGO_LOG_TRACKER_SLOW_API_ABOVE) == int:  # Making sure for integer value.
                    self._DJANGO_LOG_TRACKER_SLOW_API_ABOVE = settings.DJANGO_LOG_TRACKER_SLOW_API_ABOVE / 1000  #
                    # Converting to second.

        def lookups(self, request, model_admin):
            """
            Returns a list of tuples. The first element in each
            tuple is the coded value for the option that will
            appear in the URL query. The second element is the
            human-readable name for the option that will appear
            in the right sidebar.
            """
            slow = 'Slow'
            fast = 'Fast'
            if hasattr(settings, 'DJANGO_LOG_TRACKER_SLOW_API_ABOVE'):
                slow += ', >={}ms'.format(settings.DJANGO_LOG_TRACKER_SLOW_API_ABOVE)
                fast += ', <{}ms'.format(settings.DJANGO_LOG_TRACKER_SLOW_API_ABOVE)

            return (
                ('slow', _(slow)),
                ('fast', _(fast)),
            )

        def queryset(self, request, queryset):
            """
            Returns the filtered queryset based on the value
            provided in the query string and retrievable via
            `self.value()`.
            """
            # to decide how to filter the queryset.
            if self.value() == 'slow':
                return queryset.filter(execution_time__gte=self._DJANGO_LOG_TRACKER_SLOW_API_ABOVE)
            if self.value() == 'fast':
                return queryset.filter(execution_time__lt=self._DJANGO_LOG_TRACKER_SLOW_API_ABOVE)

            return queryset


    class LogTrackerAdmin(admin.ModelAdmin):

        def __init__(self, model, admin_site):
            super().__init__(model, admin_site)
            self._DJANGO_LOG_TRACKER_TIMEDELTA = 0
            if hasattr(settings, 'DJANGO_LOG_TRACKER_SLOW_API_ABOVE'):
                if type(settings.DJANGO_LOG_TRACKER_SLOW_API_ABOVE) == int:  # Making sure for integer value.
                    self.list_filter += (SlowAPIsFilter,)
            if hasattr(settings, 'DJANGO_LOG_TRACKER_TIMEDELTA'):
                if type(settings.DJANGO_LOG_TRACKER_TIMEDELTA) == int:  # Making sure for integer value.added_on_time
                    self._DJANGO_LOG_TRACKER_TIMEDELTA = settings.DJANGO_LOG_TRACKER_TIMEDELTA

        def added_on_time(self, obj):
            return (obj.added_on + timedelta(minutes=self._DJANGO_LOG_TRACKER_TIMEDELTA)).strftime("%d %b %Y %H:%M:%S")

        added_on_time.admin_order_field = 'added_on'
        added_on_time.short_description = 'Added on'

        list_per_page = 20
        list_display = ('id', 'status', 'api', 'method', 'headers', 'response', 'status_code',
                        'execution_time', 'client_ip_address', 'client_ip_geolocation', 'user_agent', 'added_on')
        list_filter = ('added_on', 'status_code', 'method',)
        search_fields = ('client_ip_address', 'response', 'headers', 'api', 'added_on')
        readonly_fields = (
            'execution_time', 'status', 'client_ip_address', 'api',
            'headers', 'client_ip_geolocation', 'method', 'response', 'status_code', 'added_on_time',
        )
        exclude = ('added_on',)

        change_list_template = 'log_activity_dashboard.html'
        date_hierarchy = 'added_on'

        def changelist_view(self, request, extra_context=None):
            response = super(LogTrackerAdmin, self).changelist_view(request, extra_context)
            try:
                filtered_query_set = response.context_data["cl"].queryset
            except:
                return response
            analytics_model = filtered_query_set.values('added_on__date').annotate(total=Count('id')).order_by('total')
            status_code_count_mode = filtered_query_set.values('id').values('status_code').annotate(
                total=Count('id')).order_by('status_code')
            status_code_count_keys = list()
            status_code_count_values = list()
            for item in status_code_count_mode:
                status_code_count_keys.append(item.get('status_code'))
                status_code_count_values.append(item.get('total'))
            extra_context = dict(
                analytics=analytics_model,
                status_code_count_keys=status_code_count_keys,
                status_code_count_values=status_code_count_values
            )
            response.context_data.update(extra_context)
            return response

        def get_queryset(self, request):
            return super(LogTrackerAdmin, self).get_queryset(request)

        def has_add_permission(self, request, obj=None):
            return False

        def has_change_permission(self, request, obj=None):
            return False


    admin.site.register(LogTracker, LogTrackerAdmin)
