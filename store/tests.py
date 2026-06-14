from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Create your tests here.
class AuthWorkflowTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = "admin"
        self.password = "admin123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

    def test_login_success_redirect_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.username,
                "password": self.password
            }
        )

        # harus redirect
        self.assertEqual(response.status_code, 302)

        # harus ke dashboard
        self.assertRedirects(response, reverse("dashboard"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        # biasanya redirect ke login
        self.assertEqual(response.status_code, 302)

    def test_dashboard_access_after_login(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)