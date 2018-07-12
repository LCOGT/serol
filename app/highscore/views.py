from django.utils.translation import ugettext as _
from rest_framework import serializers, generics, viewsets, status
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView

from profanityfilter import ProfanityFilter

from highscore.models import Score, LevelScore


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
            raise serializers.ValidationError(_("Try a username without bad language"))
        return value


class HighScoreView(generics.ListAPIView):
    """
    API endpoint that allows scores to be viewed or edited.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, JSONPRenderer)
    queryset = Score.objects.all().order_by('-score')[:10]
    serializer_class = ScoreSerializer

class ScheduleView(APIView):
    """
    Schedule observations given a full set of observing parameters
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, JSONPRenderer)

    def post(self, request, format=None):
        ser = ScoreSerializer(data=request.data)
        if not ser.is_valid(raise_exception=True):
            logger.error('Request was not valid')
            return Response(ser.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            ser.save()
            return Response("Success", status=status.HTTP_201_CREATED)
