from django.test import TestCase, Client
from django.contrib.auth.models import User


class TestLogTrackerAdminPanelURL(TestCase):
    def create_user(self):
        self.username = "test_admin"
        self.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=self.username)
        user.set_password(self.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.user = user

    def test_spider_admin(self):
        self.create_user()
        client = Client()
        client.login(username=self.username, password=self.password)
        admin_pages = [
            "/admin/",
            # django_log_tracker admin page for our models in here.
            "/admin/django_log_tracker/logtracker/",
        ]
        for page in admin_pages:
            resp = client.get(page)
            assert resp.status_code == 200
