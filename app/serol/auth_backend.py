from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate as dj_authenticate
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework.authtoken.models import Token
import requests
import logging

from status.models import User, Proposal

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class AddTokenBackend:

    # def authenticate(self, request):
    #     print(settings.ARCHIVE_TOKEN)

    #     return dj_authenticate(request, username, password)
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                # request.session['token'] = settings.PORTAL_TOKEN
                # request.session['archive_token'] = settings.ARCHIVE_TOKEN
                user.token = settings.PORTAL_TOKEN
                user.archive_token = settings.ARCHIVE_TOKEN
                user.save()
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class PortalBackend(object):
    """
    Authenticate against the Observing portal API.
    """

    def authenticate(self, request, username=None, password=None):
        return lco_authenticate(request, username, password)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

def lco_authenticate(request, username, password):
    token = api_auth(settings.PORTAL_TOKEN_URL, username, password)
    profile, msg = get_profile(token)
    # if msg:
    #     messages.info(request, msg)
    archivetoken = api_auth(settings.ARCHIVE_TOKEN_URL, username, password)
    if token and profile and archivetoken:
        username = profile[0]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Create a new user. There's no need to set a password
            # because Valhalla auth will always be used.
            user = User(username=username)
        user.token = token
        user.archive_token = archivetoken
        user.default_proposal = profile[2]
        user.email = profile[3]
        user.save()
        # Give the new user a Django Rest Framework token
        Token.objects.get_or_create(user=user)
        # Finally add these tokens as session variables
        request.session['token'] = token
        request.session['archive_token'] = archivetoken

        return user

    return None


def api_auth(url, username, password):
    '''
    Request authentication cookie from the Scheduler API
    '''
    try:
        r= requests.post(url,data = {
            'username': username,
            'password': password
            }, timeout=20.0);
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        return False
    except requests.exceptions.ConnectionError:
        msg = "Trouble with internet"
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
        return False, _("We are currently having problems. Please bear with us")

    if r.status_code in [200,201]:
        logger.debug('Profile successful')
        proposal = check_proposal_membership(r.json()['proposals'])
        if proposal:
            return (r.json()['username'], r.json()['tokens']['archive'], proposal, r.json()['email']), False
        else:
            logger.debug('No active proposal')
            return False, _("Please <a href='/accounts/register/'>register</a> or join a participating <a href='https://lco.global/education/partners/'>LCO education partner</a> for access to SEROL")
    else:
        logger.error("Could not get profile {}".format(r.content))
        return False, _("Please check your login details")

def check_proposal_membership(proposals):
    # Check user has a proposal we authorize
    proposals = [p['id'] for p in proposals if p['current'] == True]
    my_proposals = Proposal.objects.filter(code__in=proposals, active=True)
    if my_proposals:
        return my_proposals[0]
    else:
        return False
