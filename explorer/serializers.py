from rest_framework import serializers, status
from rest_framework.response import Response
from status.valhalla import process_observation_request, request_format
from django.conf import settings

class RequestSerializer(serializers.Serializer):
    """
    This serializer POSTing parameters to the scheduler the api.
    """
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    aperture = serializers.ChoiceField(choices=APERTURES)
    object_name = serializers.CharField()
    object_ra = serializers.FloatField()
    object_dec = serializers.FloatField()
    filters = serializers.JSONField()
    token = serializers.CharField()

    def save(self, *args, **kwargs):
        params = self.data
        obs_params = request_format(params['object_name'], params['object_ra'], params['object_dec'], params['start'], params['end'], params['filters'], kwargs['proposal'], params['aperture'])
        resp_status, resp_msg = process_observation_request(params=obs_params, token=params['token'])
        if resp_status:
            return Response('Success', status=status.HTTP_201_CREATED)
        else:
            return Response(resp_msg, status=status.HTTP_400_BAD_REQUEST)
