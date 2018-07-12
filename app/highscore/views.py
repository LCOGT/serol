from django.utils.translation import ugettext as _
from profanityfilter import ProfanityFilter
from rest_framework import serializers, generics, viewsets, status
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from highscore.models import Score, LevelScore

logger = logging.getLogger(__name__)

class ScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Score
        fields = ('score', 'username')

    def validate_username(self, value):
        """
        Check that the username doesn't have naughty words in
        """
        f = ProfanityFilter()
        if not f.is_clean(value):
            logger.error('Username contained a swear')
            raise serializers.ValidationError(_("Profane words are forbidden"))
        return value


class HighScoreView(generics.ListAPIView):
    """
    API endpoint that allows scores to be viewed
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, JSONPRenderer)
    queryset = Score.objects.all().order_by('-score')[:10]
    serializer_class = ScoreSerializer

class AddHighScoreView(APIView):
    """
    Schedule observations given a full set of observing parameters
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, JSONPRenderer)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        ser = ScoreSerializer(data=request.data)
        if not ser.is_valid(raise_exception=True):
            return Response(ser.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            ser.save()
            return Response("Success", status=status.HTTP_201_CREATED)
