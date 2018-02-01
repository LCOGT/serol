from contextlib import contextmanager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.test import TestCase
from mock import patch
from selenium import webdriver
from selenium.webdriver.support.expected_conditions import staleness_of, visibility_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
import time

from .views import RequestSerializer, ScheduleView, StatusView, save_progress
from status.models import User, Proposal

def mock_lco_authenticate(request, username, password):
    return None

def mock_submit_request(params, token):
    return True, 'XXX'

class FunctionalTest(StaticLiveServerTestCase):

    fixtures = ['mission-data.json']

    def __init__(self, *args, **kwargs):
        super(FunctionalTest, self).__init__(*args, **kwargs)

        if settings.DEBUG == False:
            settings.DEBUG = True

    def setUp(self):

        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.startup.homepage", "about:blank");
        fp.set_preference("startup.homepage_welcome_url", "about:blank");
        fp.set_preference("startup.homepage_welcome_url.additional", "about:blank");

        if not hasattr(self, 'browser'):
            firefox_capabilities = DesiredCapabilities.FIREFOX
            self.browser = webdriver.Firefox(capabilities=firefox_capabilities, firefox_profile=fp)
        self.browser.implicitly_wait(5)

        proposal_params1 = {
        'code': 'LCOEPO2014A-010',
        'active': True
        }
        p1 = Proposal(**proposal_params1)
        p1.save()

        self.username = 'ada'
        self.password = 'jenkins'
        self.email = 'ada@jenkins.org'
        self.bart = User.objects.create_user(username=self.username, email=self.email, default_proposal = p1)
        self.bart.set_password(self.password)
        self.bart.first_name= 'Ada'
        self.bart.last_name = 'Jenkins'
        self.bart.is_active=1
        self.bart.save()

    @contextmanager
    def wait_for_page_load(self, timeout=30):
        old_page = self.browser.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.browser, timeout).until(
            staleness_of(old_page)
        )

    @contextmanager
    def wait_for_js_load(self, element_id, timeout=10):
        yield WebDriverWait(self.browser, timeout).until(
            visibility_of_element_located((By.ID, element_id))


class NewVisitorTest(FunctionalTest):

    def tearDown(self):
        self.browser.refresh()
        #        self.browser.implicitly_wait(5)
        self.browser.quit()

    @patch('serol.auth_backend.lco_authenticate', mock_lco_authenticate)
    @patch('status.valhalla.submit_observation_request', mock_submit_request)
    def test_start(self):
        # Ada has heard about Serol. She goes
        # to check out its homepage
        self.browser.get(self.live_server_url)

        # She notices the page title
        self.assertIn('Serol', self.browser.title)

        # She tries to login
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_link_text('Login').click()
        username_input = self.browser.find_element_by_id("username")
        username_input.send_keys(self.username)
        password_input = self.browser.find_element_by_id("password")
        password_input.send_keys(self.password)
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_id("login-btn").click()

        # Ada navigates to the first Challenge and clicks start
        self.browser.get('{}{}'.format(self.live_server_url,'/challenge/1/'))
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_id("start-btn").click()

        # Ada wants to observe Uranus
        self.browser.find_element_by_id("target-img-Uranus").click()
        # Ada clicks submit
        with self.wait_for_js_load("submit_button", timeout=10):
            self.browser.find_element_by_id("submit_button").click()
        # Ada seems a success message
        with self.wait_for_js_load("accept_button", timeout=10):
            self.browser.find_element_by_id("accept_button").click()
        # Ada seems the Challenge submitted page and sees SEROL
        with self.wait_for_page_load(timeout=10):
            self.assertTrue(self.browser.find_element_by_id("serol-figure"))

    @patch('serol.auth_backend.lco_authenticate', mock_lco_authenticate)
    @patch('status.valhalla.submit_observation_request', mock_submit_request)
    def test_observe(self):
        # Ada has heard about Serol. She goes
        # to check out its homepage
        self.browser.get(self.live_server_url)
        # She notices the page title
        self.assertIn('Serol', self.browser.title)
        # She tries to login
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_link_text('Login').click()
        username_input = self.browser.find_element_by_id("username")
        username_input.send_keys(self.username)
        password_input = self.browser.find_element_by_id("password")
        password_input.send_keys(self.password)
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_id("login-btn").click()

        # Ada navigates to the first Challenge and clicks start
        self.browser.get('{}{}'.format(self.live_server_url,'/challenge/1/'))

if __name__ == '__main__':
    unittest.main(warnings='ignore')
