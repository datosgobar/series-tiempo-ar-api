#!coding=utf8
import os
import mock

import sendfile
from django.http import FileResponse
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class AnalyticsDownloadTests(TestCase):

    def test_download_when_not_staff(self):
        response = self.client.get(reverse('analytics:read_analytics'))

        # Expected: admin login redirect
        self.assertEqual(response.status_code, 302)

    def test_download_as_staff(self):
        user = User(username='user', password='pass', email='mail@test.com', is_staff=True)
        user.save()
        self.client.force_login(user)

        response_file = open(os.path.join(samples_dir, 'sample_analytics_dump.csv'))
        sendfile.sendfile = mock.Mock(return_value=FileResponse(response_file))
        response = self.client.get(reverse('analytics:read_analytics'))

        self.assertEqual(response.status_code, 200)

        with open(os.path.join(samples_dir, 'sample_analytics_dump.csv')) as response_file:
            response_content = list(response.streaming_content)[0]  # Unwrap iterable
            self.assertEqual(response_content, response_file.read())
