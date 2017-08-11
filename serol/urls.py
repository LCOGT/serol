from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles import views
from django.contrib.auth.views import login, logout
from django.conf import settings
from django.views.generic import TemplateView

from status.views import ScheduleView, StatusView
from explorer.views import MissionView, ChallengeRedirectView, ChallengeView


urlpatterns = [
    url(r'^mission/(?P<pk>[0-9]+)/$', MissionView.as_view(), name="mission"),
    url(r'^challenge/(?P<pk>[0-9]+)/start/$', ChallengeView.as_view(), {'mode':'start'}, name="challenge-start"),
    url(r'^challenge/(?P<pk>[0-9]+)/observe/$', ChallengeView.as_view(), {'mode':'observe'}, name="challenge-observe"),
    url(r'^challenge/(?P<pk>[0-9]+)/identify/$', ChallengeView.as_view(), {'mode':'identify'}, name="challenge-identify"),
    url(r'^challenge/(?P<pk>[0-9]+)/analyse/$', ChallengeView.as_view(), {'mode':'analyse'}, name="challenge-analyse"),
    url(r'^challenge/(?P<pk>[0-9]+)/investigate/$', ChallengeView.as_view(), {'mode':'investigate'}, name="challenge-investigate"),
    url(r'^challenge/(?P<pk>[0-9]+)/$', ChallengeRedirectView.as_view(), name="challenge"),
    url(r'^status/(?P<pk>[0-9]+)/$', StatusView.as_view(), name="status"),
    url(r'^api/schedule/$', ScheduleView.as_view(), name='schedule'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', login, {'template_name': 'explorer/login.html'}, name='auth_login'),
    url(r'^logout/$', logout, {'template_name': 'explorer/logout.html'}, name='auth_logout'),
    url(r'^$', TemplateView.as_view(template_name="explorer/home.html"), name='home'),

]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]
