from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.views.generic import TemplateView

from status.views import ScheduleView, StatusView
from explorer.views import MissionView, ChallengeRedirectView, ChallengeView


urlpatterns = [
    url(r'^mission/(?P<pk>[0-9]+)/$', MissionView.as_view(), name="mission"),
    url(r'^challenge/(?P<pk>[0-9]+)/start/$', ChallengeView.as_view(), {'mode':'start'}, name="start"),
    url(r'^challenge/(?P<pk>[0-9]+)/observe/$', ChallengeView.as_view(), {'mode':'observe'}, name="observe"),
    url(r'^challenge/(?P<pk>[0-9]+)/identify/$', ChallengeView.as_view(), {'mode':'identify'}, name="identify"),
    url(r'^challenge/(?P<pk>[0-9]+)/analyse/$', ChallengeView.as_view(), {'mode':'analyse'}, name="analyse"),
    url(r'^challenge/(?P<pk>[0-9]+)/investigate/$', ChallengeView.as_view(), {'mode':'investigate'}, name="investigate"),
    url(r'^challenge/(?P<pk>[0-9]+)/submitted/$', ChallengeView.as_view(), {'mode':'submitted'}, name="submitted"),
    url(r'^challenge/(?P<pk>[0-9]+)/$', ChallengeRedirectView.as_view(), name="challenge"),
    url(r'^status/(?P<userrequestid>[0-9]+)/$', StatusView.as_view(), name="status"),
    url(r'^api/schedule/$', ScheduleView.as_view(), name='schedule'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', LoginView.as_view(template_name='explorer/login.html'), name='auth_login'),
    url(r'^logout/$', LogoutView.as_view(template_name= 'explorer/logout.html'), name='auth_logout'),
    url(r'^$', TemplateView.as_view(template_name="explorer/home.html"), name='home'),

]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]
