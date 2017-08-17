from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
import requests
import logging

logger = logging.getLogger(__name__)

class ValhallaBackend(object):
    """
    Authenticate against the Vahalla API.
    """

    def authenticate(self, request, username=None, password=None):
        status, resp = valhalla_auth(username, password)
        if status:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because Valhalla auth will always be used.
                user = User(username=username)
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

def valhalla_auth(username, password):
    '''
    Request authentication cookie from the Scheduler API
    '''
    url = settings.PORTAL_TOKEN_URL
    try:
        r= requests.post(url,data = {
            'username': username,
            'password': password
            }, timeout=20.0);
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        logger.debug('Login successful for {}'.format(username))
        return True, r.json()['token']
    else:
        logger.error("Could not login {}: {}".format(username, r.json()['non_field_errors']))
        return False, r.content
