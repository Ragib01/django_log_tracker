from queue import Queue
import time
from django.conf import settings
from threading import Thread
from django.db.utils import OperationalError

from .models import LogTracker


class InsertLogIntoDatabase(Thread):

    def __init__(self):
        super().__init__()

        self.DJANGO_LOG_TRACKER_DEFAULT_DATABASE = 'default'
        if hasattr(settings, 'DJANGO_LOG_TRACKER_DEFAULT_DATABASE'):
            self.DJANGO_LOG_TRACKER_DEFAULT_DATABASE = settings.DJANGO_LOG_TRACKER_DEFAULT_DATABASE

        self.DJANGO_LOG_TRACKER_QUEUE_MAX_SIZE = 50  # Default queue size 50
        if hasattr(settings, 'DJANGO_LOG_TRACKER_QUEUE_MAX_SIZE'):
            self.DJANGO_LOG_TRACKER_QUEUE_MAX_SIZE = settings.DJANGO_LOG_TRACKER_QUEUE_MAX_SIZE

        if self.DJANGO_LOG_TRACKER_QUEUE_MAX_SIZE < 1:
            raise Exception("""
            DJANGO LOG TRACKER API LOGGER EXCEPTION
            Value of DJANGO_LOG_TRACKER_QUEUE_MAX_SIZE must be greater than 0
            """)

        self.DJANGO_LOG_TRACKER_INTERVAL = 10  # Default DB insertion interval is 10 seconds.
        if hasattr(settings, 'DJANGO_LOG_TRACKER_INTERVAL'):
            self.DJANGO_LOG_TRACKER_INTERVAL = settings.DJANGO_LOG_TRACKER_INTERVAL

            if self.DJANGO_LOG_TRACKER_INTERVAL < 1:
                raise Exception("""
                DJANGO_LOG_TRACKER API LOGGER EXCEPTION
                Value of DJANGO_LOG_TRACKER_INTERVAL must be greater than 0
                """)

        self._queue = Queue(maxsize=self.DJANGO_LOG_TRACKER_QUEUE_MAX_SIZE)

    def run(self) -> None:
        self.start_queue_process()

    def put_log_data(self, data):
        self._queue.put(LogTracker(**data))

        if self._queue.qsize() >= self.DJANGO_LOG_TRACKER_QUEUE_MAX_SIZE:
            self._start_bulk_insertion()

    def start_queue_process(self):
        while True:
            time.sleep(self.DJANGO_LOG_TRACKER_INTERVAL)
            self._start_bulk_insertion()

    def _start_bulk_insertion(self):
        bulk_item = []
        while not self._queue.empty():
            bulk_item.append(self._queue.get())
        if bulk_item:
            self._insert_into_data_base(bulk_item)

    def _insert_into_data_base(self, bulk_item):
        try:
            LogTracker.objects.using(self.DJANGO_LOG_TRACKER_DEFAULT_DATABASE).bulk_create(bulk_item)
        except OperationalError:
            raise Exception("""
            DJANGO LOG TRACKER EXCEPTION
            Model does not exists.
            Did you forget to migrate?
            """)
        except Exception as e:
            print('DJANGO LOG TRACKER EXCEPTION:', e)
