from contextlib import contextmanager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.test import TestCase
from mock import patch
from model_bakery import baker
from selenium import webdriver
from selenium.webdriver.support.expected_conditions import staleness_of, visibility_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
import time

from serol.basetest import FunctionalTest
from status.tests import mock_lco_authenticate
from serol.mocks import *
from .utils import *

from .models import *

import factory

class MissionFactory(factory.Factory):
    class Meta:
        model = Mission

class ChallengeFactory(factory.Factory):
    class Meta:
        model = Challenge

class AnswerFactory(factory.Factory):
    class Meta:
        model = Answer

class BrowseSiteTest(FunctionalTest):

        @patch('serol.auth_backend.lco_authenticate', mock_lco_authenticate)
        def test_check_user_links(self):
            # Ada has heard about Serol. She goes
            # to check out its homepage
            self.login(username=self.username, password=self.password)
            self.browser.get(self.live_server_url)
            # She clicks on Missions
            with self.wait_for_page_load(timeout=10):
                self.browser.find_element_by_link_text("Missions").click()

            self.assertIn('Missions', self.browser.title)
            # Ada has access to Mission 1
            btn = self.browser.find_element_by_id("mission-btn-1")
            self.assertIn('START', btn.text)
            # Ada does not have access to Mission 2 or 3
            btn = self.browser.find_element_by_id("mission-btn-2")
            self.assertIn('unlock', btn.text)

            btn = self.browser.find_element_by_id("mission-btn-3")
            self.assertIn('unlock', btn.text)

            with self.wait_for_page_load(timeout=10):
                self.browser.find_element_by_link_text("My Progress").click()

            self.assertIn('Stickers', self.browser.title)

            # Check we have more than 1 locked challenge
            self.browser.find_element_by_css_selector("img.locked-sticker")

            with self.wait_for_page_load(timeout=10):
                self.browser.find_element_by_partial_link_text("START").click()

            self.assertIn("Planets", self.browser.title)

            self.tearDown()

        def test_check_static_pages(self):
            self.browser.get(self.live_server_url)

            # She clicks on Resources
            with self.wait_for_page_load(timeout=10):
                self.browser.find_element_by_link_text('About Serol').click()
            self.assertIn('About', self.browser.title)
            # She clicks on Resources
            with self.wait_for_page_load(timeout=10):
                self.browser.find_element_by_link_text('Resources').click()
            self.assertIn('Resources', self.browser.title)

            # She clicks on education
            with self.wait_for_page_load(timeout=10):
                self.browser.find_element_by_link_text('Videos').click()
            self.assertIn('Film', self.browser.title)

            self.tearDown()

class UtilsTest(TestCase):

    def setUp(self):
        self.user = baker.make('status.User', mission_1=True)
        # self.make_basic_site()

    def test_deg_to_hms_plain_fail(self):
        ra, dec = deg_to_hms_plain("x","x")
        self.assertEqual(ra, "0")
        self.assertEqual(dec, "0")

    def test_deg_to_hms_plain_success(self):
        ra, dec = deg_to_hms_plain(12.2, 20.2)
        self.assertEqual(ra, "0 : 48 : 48")
        self.assertEqual(dec, "20 : 11 : 60")

    def test_completed_missions(self):
        missions = completed_missions(self.user)
        self.assertEqual(missions, [1])

    def test_target_icon_fail(self):

class ViewsTest(TestCase):


    def test_add_answers(self):
        resp = add_answers(answers, self.user)
