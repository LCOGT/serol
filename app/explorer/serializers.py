from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from profanityfilter import ProfanityFilter
from rest_framework import serializers, generics, viewsets, status
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from explorer.models import Fact

from highscore.models import Score, LevelScore

logger = logging.getLogger(__name__)

class FactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Fact
        fields = '__all__'

class FactsView(generics.ListAPIView):
    """
    API endpoint that allows scores to be viewed
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    serializer_class = FactSerializer
    queryset = Fact.objects.all().order_by('?')
