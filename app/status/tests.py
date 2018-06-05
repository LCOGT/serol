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
from status.models import User, Proposal, Progress
from status.valhalla import process_observation_request, request_format, format_sidereal_object

def mock_lco_authenticate(request, username, password):
    return None

def mock_submit_request(params, token):
    return True, '000'

def mock_submit_request_check_proposal(params, token):
    if params['proposal'] == 'LCOEPO2018A-001':
        return True, 'XXX'
    elif params['proposal'] == 'LCOEPO2018A-002':
        return False, 'Wrong proposal'


class ScheduleTest(TestCase):
    def setUp(self):
        proposal_params1 = {
        'code': 'LCOEPO2018A-001',
        'active': True
        }
        p1 = Proposal(**proposal_params1)
        p1.save()

        proposal_params2 = {
        'code': 'LCOEPO2018A-002',
        'active': True
        }
        p2 = Proposal(**proposal_params2)
        p2.save()

        self.proposal1 = p1
        self.proposal2 = p2
        self.username = 'ada'
        self.password = 'jenkins'
        self.email = 'ada@jenkins.org'
        self.ada = User.objects.create_user(username=self.username, email=self.email, default_proposal = p2)
        self.ada.set_password(self.password)
        self.ada.first_name= 'Ada'
        self.ada.last_name = 'Jenkins'
        self.ada.is_active=1
        self.ada.save()

    def test_request_format(self):
        # Check the user's default proposal is the one we get in the request format_moving_object
        object_name = 'M1'
        object_ra = 83.6330833
        object_dec = 22.0145000
        start = '2018-02-14T00:00:00'
        end = '2018-02-28T00:00:00'
        filters = [{'exposure': 10.0,'name':'v'},{'exposure': 20.0,'name':'rp'},{'exposure': 30.0,'name':'b'}]

        target = format_sidereal_object(object_name, object_ra, object_dec)
        params = request_format(target, start, end, filters, self.ada.default_proposal.code)

        self.assertEqual(params['proposal'], self.ada.default_proposal.code)
        for i, mol in enumerate(params['requests'][0]['molecules']):
            self.assertEqual(mol['exposure_time'],  filters[i]['exposure'])
            self.assertEqual(mol['filter'],  filters[i]['name'])
        self.assertEqual(params['requests'][0]['target']['name'],object_name)

    @patch('status.valhalla.submit_observation_request', mock_submit_request_check_proposal)
    def test_wrong_proposal(self):
        params = {
        'object_name': 'M1',
        'object_ra': 83.6330833,
        'object_dec': 22.0145000,
        'start': '2018-02-14T00:00:00',
        'end': '2018-02-28T00:00:00',
        'filters': [{'exposure': 10.0, 'name':'v'}],
        'target_type' : 'static',
        'aperture' : '0m4',
        'token' : 'XXX'
        }

        params['proposal'] = self.ada.default_proposal.code

        resp_status, resp_msg, target = process_observation_request(params)

        self.assertFalse(resp_status)

    @patch('status.valhalla.submit_observation_request', mock_submit_request_check_proposal)
    def test_correct_proposal(self):
        self.ada.default_proposal = self.proposal1
        self.ada.save()
        params = {
        'object_name': 'M1',
        'object_ra': 83.6330833,
        'object_dec': 22.0145000,
        'start': '2018-02-14T00:00:00',
        'end': '2018-02-28T00:00:00',
        'filters': [{'exposure': 10.0, 'name':'v'}],
        'target_type' : 'static',
        'aperture' : '0m4',
        'token' : 'XXX'
        }

        params['proposal'] = self.ada.default_proposal.code

        resp_status, resp_msg, target = process_observation_request(params)

        self.assertTrue(resp_status)
        self.assertEqual(target, params['object_name'])


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
        self.ada = User.objects.create_user(username=self.username, email=self.email, default_proposal = p1)
        self.ada.set_password(self.password)
        self.ada.first_name= 'Ada'
        self.ada.last_name = 'Jenkins'
        self.ada.is_active=1
        self.ada.save()

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
            )

class NewVisitorTest(FunctionalTest):

    def tearDown(self):
        self.browser.refresh()
        #        self.browser.implicitly_wait(5)
        self.browser.quit()

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
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_id("start-btn").click()

        # Ada wants to observe Uranus
        self.browser.find_element_by_id("target-img-2").click()
        # Ada clicks submit
        with self.wait_for_js_load("submit_button", timeout=10):
            self.browser.find_element_by_id("submit_button").click()
        # Ada sees a success message
        with self.wait_for_js_load("accept_button", timeout=10):
            self.browser.find_element_by_id("accept_button").click()
        # Ada sees the Challenge submitted page and sees SEROL
        with self.wait_for_page_load(timeout=10):
            self.assertTrue(self.browser.find_element_by_id("serol-figure"))

        progress = Progress.objects.get(user=self.ada, challenge__id=1)
        self.assertEqual(progress.target, 'Uranus')
        self.assertEqual(progress.requestid, '000')

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

if __name__ == '__main__':
    unittest.main(warnings='ignore')
