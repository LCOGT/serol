from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from profanityfilter import ProfanityFilter
from rest_framework import serializers, generics, viewsets, status
from rest_framework.authentication import TokenAuthentication
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
        return check_username(value)

    def validate_score(self, value):
        if not value:
            raise serializers.ValidationError(_("Score is required"))
        return value

class LevelScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = LevelScore
        fields = ('score', 'username','level', 'user')

    def validate_username(self, value):
        return check_username(value)

    def validate_score(self, value):
        if not value:
            raise serializers.ValidationError(_("Score is required"))
        return value

    def validate_level(self, value):
        if not value:
            raise serializers.ValidationError(_("Level is required"))
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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        data = request.data
        if request.user.username == 'game':
            anonymous = True
            ser = ScoreSerializer(data=data)

        else:
            anonymous = False
            data['user'] = request.user.id
            try:
                oldscore = LevelScore.objects.get(user=request.user,level=data['level'])
                ser = LevelScoreSerializer(oldscore, data=data)
            except ObjectDoesNotExist:
                ser = LevelScoreSerializer(data=data)

        if not ser.is_valid(raise_exception=True):
            return Response(ser.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            ser.save()
            if not anonymous:
                auth_user_high_score(user=request.user)
            return Response("Success", status=status.HTTP_201_CREATED)

def auth_user_high_score(user):
    scores = LevelScore.objects.filter(user=user)
    if scores.count() == 0:
        return False

    topscore = scores.aggregate(sum=Sum('score'))
    score = Score()
    score.score = topscore['sum']
    score.username = scores[0].username
    score.save()
    return True

def check_username(value):
    """
    Check that the username doesn't have naughty words in
    """
    f = ProfanityFilter()
    if not f.is_clean(value):
        logger.error('Username contained a swear')
        raise serializers.ValidationError(_("Profane words are forbidden"))
    return value
