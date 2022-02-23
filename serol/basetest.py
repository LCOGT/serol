from contextlib import contextmanager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.support.expected_conditions import staleness_of, visibility_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from mock import patch

from serol.mocks import *
from status.models import User, Proposal

class FunctionalTest(StaticLiveServerTestCase):

    fixtures = ['mission-data.json','pages.json', 'stickers.json']

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

    @patch('serol.auth_backend.lco_authenticate', mock_lco_authenticate)
    def login(self, username, password):
        self.browser.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.browser.find_element_by_id("username")
        username_input.send_keys(username)
        password_input = self.browser.find_element_by_id("password")
        password_input.send_keys(password)
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_id("login-btn").click()

    def tearDown(self):
        self.browser.quit()
