from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# Create your tests here.
class GetCookieViewTestCase(TestCase):

    def test_get_cookie_view(self):
        response = self.client.get(reverse("myauth:get-cookie"))
        self.assertContains(response, "Cookie value")