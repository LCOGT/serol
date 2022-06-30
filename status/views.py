import time
import json
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django_registration.forms import RegistrationForm
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework import status, serializers
from user_messages import api

from status.models import Progress, User

from status.schedule import process_observation_request, get_observation_status, \
    get_observation_frameid, auto_schedule, submit_observation_request


class SerolUserForm(RegistrationForm):
    class Meta:
        model = User
        fields = ('username','password1','password2','email')

class RequestSerializer(serializers.Serializer):
    """
    POSTing parameters to the Observing Portal api.
    """
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    aperture = serializers.CharField()
    target_type = serializers.ChoiceField(choices=(('moving', 'moving'),('sidereal', 'sidereal'),('moon','moon')))
    object_name = serializers.CharField()
    object_ra = serializers.FloatField(required=False)
    object_dec = serializers.FloatField(required=False)
    filters = serializers.JSONField(required=False)
    token = serializers.CharField()
    challenge = serializers.IntegerField()

class MoonSerializer(serializers.Serializer):
    proposal = serializers.CharField(max_length=100)
    target_type = serializers.CharField(max_length=100)

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
            user_logged_in = request.user.is_authenticated
            if not token and user_logged_in:
                params['token'] = settings.PORTAL_TOKEN
            elif not token and not user_logged_in:

                return Response("Not authenticated.", status=status.HTTP_401_UNAUTHORIZED)
            # Send to Portal API
            if request.user.default_proposal:
                params['proposal'] = request.user.default_proposal.code
            else:
                params['proposal'] = settings.DEFAULT_PROPOSAL
            resp_status, resp_msg, target, resp_group = process_observation_request(params)
            if not resp_status:

                return Response(resp_msg, status=status.HTTP_400_BAD_REQUEST)

            # As long as we can a good response from the API, save the progress state
            reqids = json.dumps(resp_msg)
            resp_prog = save_progress(challenge=params['challenge'], user=request.user, request_id=reqids, target=target, request_group=resp_group)
            if resp_status and resp_prog:

                return Response("Success", status=status.HTTP_201_CREATED)
            else:

                return Response("Manipulating status", status=status.HTTP_400_BAD_REQUEST)


class StatusView(APIView):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, progressid, requestid, format=None):
        token = check_token(request.user)
        return update_status(progressid=progressid, requestid=requestid, token=token)

class RemoveMessages(APIView):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request):
        try:
            msgs = api.get_messages(user=request.user)
            for m in msgs:
                m.delete()
        except TypeError:
            return Response('No user supplied', status=status.HTTP_400_BAD_REQUEST)
        return Response('Success', status=status.HTTP_200_OK)

class UpdateBadge(APIView):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, progressid):
        Progress.objects.filter(user=request.user, id=progressid).update(badge_shown=True)
        return Response(f'Progress {progressid} badge status updated', status=status.HTTP_200_OK)

class AllImages(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "status/all_images.html"
    model = Progress
    paginate_by = 12

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return super().get_queryset().filter(image_file__isnull=False).order_by('-last_update')

@method_decorator(csrf_exempt, name='dispatch')
class ScheduleMoon(APIView):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def post(self, request):
        serializer = MoonSerializer(data=request.data)
        if serializer.is_valid():
            if not request.META.get('HTTP_AUTHORIZATION',None):
                return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
            data = {
            'target_type'   : serializer.data['target_type'],
            'proposal'      : serializer.data['proposal'],
            'token'         : request.META['HTTP_AUTHORIZATION'].split(' ')[1]
            }
            resp_status, resp_msg, target, resp_group = process_observation_request(data)
            return Response(resp_msg, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def update_status(progressid, requestid, token):
    try:
        progress = Progress.objects.get(id=progressid)
    except:
        return Response("Progress object not found", status=status.HTTP_404_NOT_FOUND)
    if progress.status != 'Submitted':
        return Response("Status retrieved", status=status.HTTP_200_OK)
    requestid, state = get_observation_status(requestid=requestid, token=token)
    if state == 'PENDING':
        return Response("Not observed yet", status=status.HTTP_403_FORBIDDEN)
    elif not requestid:
        return Response("Problem with the status", status=status.HTTP_403_FORBIDDEN)
    else:
        if state == 'COMPLETED':
            data = get_observation_frameid(requestid=requestid, token=token)
            if data:
                progress.frameids = data['frameid']
                progress.ra = data['ra']
                progress.dec = data['dec']
                progress.obsdate = data['date'][0:19]
                progress.observed()
            progress.requestid = json.dumps([requestid])
        elif state == 'WINDOW_EXPIRED' or state == 'CANCELED' or state == 'FAILURE_LIMIT_REACHED':
            progress.failed()
        progress.save()
        return Response("Status updated", status=status.HTTP_200_OK)

def save_progress(challenge, user, request_id, target, request_group):
    '''
    Save Progress model
    '''
    try:
        progress = Progress.objects.get(challenge=challenge, user=user)
    except ObjectNotFound:
        return False
    progress.requestgroup = request_group
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
    return token
