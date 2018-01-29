from django.shortcuts import render
from django.conf import settings
import time

from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework import status, serializers

from status.models import Progress

from status.valhalla import process_observation_request, get_observation_status


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

    # def save(self, *args, **kwargs):
    #     params = self.data
    #     resp_status, resp_msg = process_observation_request(params)
    #     if not resp_status:
    #         return Response(resp_msg, status=status.HTTP_400_BAD_REQUEST)
    #     resp_prog = save_progress(challenge=params['challenge'], user=kwargs['user'], request_id=resp_msg, target=params['object_name'])
    #     if resp_status and resp_prog:
    #         return Response("Success", status=status.HTTP_201_CREATED)
    #     else:
    #         return Response("Manipulating status", status=status.HTTP_400_BAD_REQUEST)


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
            token = request.data.get('token', False)
            if not token:

                return Response("Not authenticated.", status=status.HTTP_401_UNAUTHORIZED)
            # Send to Valhalla API
            params = ser.data
            resp_status, resp_msg = process_observation_request(params)
            if not resp_status:

                return Response(resp_msg, status=status.HTTP_400_BAD_REQUEST)

            # As long as we can a good response from the API, save the progress state
            resp_prog = save_progress(challenge=params['challenge'], user=request.user, request_id=resp_msg, target=params['object_name'])
            if resp_status and resp_prog:

                return Response("Success", status=status.HTTP_201_CREATED)
            else:

                return Response("Manipulating status", status=status.HTTP_400_BAD_REQUEST)


class StatusView(APIView):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, userrequestid, format=None):
        requestid, state = get_observation_status(userrequestid, request.user.token)
        if state == 'PENDING':
            return Response("No observed yet", status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                progress = Progress.objects.get(userrequestid=userrequestid,user=request.user)
            except:
                return Response("Progress object not found", status=status.HTTP_404_NOT_FOUND)
            progress.requestids = requestid
            if state == 'COMPLETED':
                progress.observed()
            elif state == 'FAILED':
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
    progress.userrequestid = request_id
    progress.target = target
    progress.submit()
    progress.save()
    return True
