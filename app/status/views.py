from django.shortcuts import render
from django.conf import settings
import time

from registration.forms import RegistrationForm
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework import status, serializers

from status.models import Progress, User

from status.valhalla import process_observation_request, get_observation_status, get_observation_frameid


class SerolUserForm(RegistrationForm):
    class Meta:
        model = User
        fields = ('username','password1','password2','email')

class RequestSerializer(serializers.Serializer):
    """
    POSTing parameters to the Valhalla api.
    """
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    aperture = serializers.CharField()
    target_type = serializers.ChoiceField(choices=(('moving', 'moving'),('sidereal', 'sidereal')))
    object_name = serializers.CharField()
    object_ra = serializers.FloatField(required=False)
    object_dec = serializers.FloatField(required=False)
    filters = serializers.JSONField(required=False)
    token = serializers.CharField()
    challenge = serializers.IntegerField()


class ScheduleView(APIView):
    """
    Schedule observations given a full set of observing parameters
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def post(self, request, format=None):
        ser = RequestSerializer(data=request.data)
        if not ser.is_valid(raise_exception=True):
            logger.error('Request was not valid')
            return Response(ser.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            params = ser.data
            token = request.user.token
            user_logged_in = request.user.is_authenticated()
            if not token and user_logged_in:
                params['token'] = settings.PORTAL_TOKEN
            elif not token and not user_logged_in:

                return Response("Not authenticated.", status=status.HTTP_401_UNAUTHORIZED)
            # Send to Valhalla API
            if request.user.default_proposal:
                params['proposal'] = request.user.default_proposal.code
            else:
                params['proposal'] = settings.DEFAULT_PROPOSAL
            resp_status, resp_msg, target = process_observation_request(params)
            if not resp_status:

                return Response(resp_msg, status=status.HTTP_400_BAD_REQUEST)

            # As long as we can a good response from the API, save the progress state
            resp_prog = save_progress(challenge=params['challenge'], user=request.user, request_id=resp_msg, target=target)
            if resp_status and resp_prog:

                return Response("Success", status=status.HTTP_201_CREATED)
            else:

                return Response("Manipulating status", status=status.HTTP_400_BAD_REQUEST)


class StatusView(APIView):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, requestid, format=None):
        token, archive_token = check_token(request.user)
        return update_status(requestid=requestid, token=request.user.token, archive_token=request.user.archive_token)


def update_status(requestid, token, archive_token):
    try:
        progress = Progress.objects.get(requestid=requestid)
    except:
        return Response("Progress object not found", status=status.HTTP_404_NOT_FOUND)
    if progress.status != 'Submitted':
        return Response("Status mismatch", status=status.HTTP_403_FORBIDDEN)
    requestid, state = get_observation_status(requestid=requestid, token=token)
    if state == 'PENDING':
        return Response("Not observed yet", status=status.HTTP_403_FORBIDDEN)
    elif not requestid:
        return Response("Problem with the status", status=status.HTTP_403_FORBIDDEN)
    else:
        if state == 'COMPLETED':
            frameid = get_observation_frameid(requestid=requestid, token=archive_token)
            if frameid:
                progress.frameids = frameid
                progress.observed()
        elif state == 'WINDOW_EXPIRED' or state == 'CANCELED':
            progress.failed()
        progress.save()
        return Response("Status updated", status=status.HTTP_200_OK)

def save_progress(challenge, user, request_id, target):
    '''
    Save Progress model
    '''
    try:
        progress = Progress.objects.get(challenge=challenge, user=user)
    except ObjectNotFound:
        return False
    progress.requestid = request_id
    progress.target = target
    progress.submit()
    progress.save()
    return True

def check_token(user):
    if not user.token:
        token = settings.PORTAL_TOKEN
    else:
        token = user.token
    if not user.archive_token:
        archive_token = settings.ARCHIVE_TOKEN
    else:
        archive_token = user.archive_token
    return token, archive_token
