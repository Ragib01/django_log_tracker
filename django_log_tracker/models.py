from django.db import models

from .utils import database_log_enabled


if database_log_enabled():
    """
    Load models only if DJANGO_LOG_TRACKER_DATABASE is True
    """
    class BaseModel(models.Model):
        id = models.BigAutoField(primary_key=True)

        added_on = models.DateTimeField()

        def __str__(self):
            return str(self.id)

        class Meta:
            abstract = True
            ordering = ('-added_on',)


    class LogTracker(BaseModel):
        status = models.CharField(max_length=255, null=True)
        api = models.CharField(max_length=1024, null=True, help_text='API URL')
        method = models.CharField(max_length=20, null=True, db_index=True)
        headers = models.TextField(null=True)
        client_ip_address = models.CharField(max_length=50, null=True)
        client_ip_geolocation = models.TextField(null=True)
        response = models.TextField(null=True)
        status_code = models.PositiveSmallIntegerField(blank=True, help_text='Response status code', db_index=True)
        execution_time = models.DecimalField(blank=True, decimal_places=5, max_digits=8,
                                             help_text='Server execution time (Not complete response time.)')
        user_agent = models.TextField(null=True)

        def __str__(self):
            return self.api

        class Meta:
            db_table = 'django_logs'
            verbose_name = 'Log'
            verbose_name_plural = 'Logs'
