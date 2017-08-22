from django.conf import settings
from django.contrib.auth.hashers import check_password
import requests
import logging

from status.models import User

logger = logging.getLogger(__name__)

class ValhallaBackend(object):
    """
    Authenticate against the Vahalla API.
    """

    def authenticate(self, request, username=None, password=None):
        token = valhalla_auth(username, password)
        profile = get_profile(token)
        if token and profile:
            username = profile[0]
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because Valhalla auth will always be used.
                user = User(username=username)
            user.token = token
            user.archive_token = profile[1]
            user.save()
            # Finally add these tokens as session variables
            request.session['token'] = token
            request.session['archive_token'] = profile
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
        return False

    if r.status_code in [200,201]:
        logger.debug('Login successful for {}'.format(username))
        return r.json()['token']
    else:
        logger.error("Could not login {}: {}".format(username, r.json()['non_field_errors']))
        return False

def get_profile(token):
    url = settings.PORTAL_PROFILE_URL
    token = {'Authorization': 'Token {}'.format(token)}
    try:
        r = requests.get(url, headers=token, timeout=20.0);
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        return False

    if r.status_code in [200,201]:
        logger.debug('Profile successful')
        return (r.json()['username'], r.json()['tokens']['archive'])
    else:
        logger.error("Could not get profile {}".format(r.content))
        return False
