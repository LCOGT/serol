from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.flatpages.views import flatpage
from django.contrib.staticfiles import views
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token

from status.views import ScheduleView, StatusView
from explorer.views import MissionView, MissionListView, ChallengeRedirectView, \
    ChallengeView, AnalyseView, ChallengeSummary, ChallengeRetry, NextChallengeView
from explorer.serializers import FactsView
from stickers.views import StickerView
from highscore.views import HighScoreView, AddHighScoreView


urlpatterns = [
    url(r'^about/$', flatpage, {'url': '/about/'}, name='about'),
    url(r'^videos/$', flatpage, {'url': '/videos/'}, name='videos'),
    url(r'^join/$', flatpage, {'url': '/join/'}, name='join'),
    url(r'^game/$', flatpage, {'url': '/game/'}, name='game'),
    url(r'^resources/$', flatpage, {'url': '/resources/'}, name='resources'),
    url(r'^resources/workshops/$', flatpage, {'url': '/resources/workshops/'}, name='resources'workshops/),
    url(r'^getting-started/$', flatpage, {'url' : '/getting-started/'}, name='getting-started'),
    url(r'^page/(?P<url>.*/)$', flatpage),
    url(r'^mission/(?P<pk>[0-9]+)/$', MissionView.as_view(), name="mission"),
    url(r'^mission/(?P<mission_num>[0-9]+)/next/$', NextChallengeView.as_view(), name="challenge-next"),
    url(r'^missions/$', MissionListView.as_view(), name="missions"),
    url(r'^challenge/(?P<pk>[0-9]+)/start/$', ChallengeView.as_view(), {'mode':'start'}, name="start"),
    url(r'^challenge/(?P<pk>[0-9]+)/observe/$', ChallengeView.as_view(), {'mode':'observe'}, name="observe"),
    url(r'^challenge/(?P<pk>[0-9]+)/identify/$', ChallengeView.as_view(), {'mode':'identify'}, name="identify"),
    url(r'^challenge/(?P<pk>[0-9]+)/analyse/$', AnalyseView.as_view(), name="analyse"),
    url(r'^challenge/(?P<pk>[0-9]+)/investigate/$', ChallengeView.as_view(), {'mode':'investigate'}, name="investigate"),
    url(r'^challenge/(?P<pk>[0-9]+)/submitted/$', ChallengeView.as_view(), {'mode':'submitted'}, name="submitted"),
    url(r'^challenge/(?P<pk>[0-9]+)/summary/$', ChallengeSummary.as_view(), {'mode':'summary'}, name="summary"),
    url(r'^challenge/(?P<pk>[0-9]+)/failed/$', ChallengeView.as_view(), {'mode':'failed'}, name="failed"),
    url(r'^challenge/(?P<pk>[0-9]+)/retry/$', ChallengeRetry.as_view(), name="retry"),
    url(r'^challenge/(?P<pk>[0-9]+)/$', ChallengeRedirectView.as_view(), name="challenge"),
    url(r'^stickers/$', StickerView.as_view(), name='stickers'),
    url(r'^api/status/(?P<requestid>[0-9]+)/$', StatusView.as_view(), name="status"),
    url(r'^api/facts/$',FactsView.as_view(), name="facts"),
    url(r'^api/schedule/$', ScheduleView.as_view(), name='schedule'),
    url(r'^api/highscore/add/$', AddHighScoreView.as_view() , name='highscore-add'),
    url(r'^api/highscore/leaders/$', HighScoreView.as_view()),
    url(r'^api-auth-token/$', obtain_auth_token),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', LoginView.as_view(template_name='explorer/login.html'), name='auth_login'),
    url(r'^logout/$', LogoutView.as_view(template_name= 'explorer/logout.html'), name='auth_logout'),
    url(r'^$', TemplateView.as_view(template_name="explorer/home.html"), name='home'),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
