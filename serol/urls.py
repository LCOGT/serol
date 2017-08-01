from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles import views
from django.conf import settings
from django.views.generic import TemplateView

from explorer.views import MissionView, ChallengeView


urlpatterns = [
    url(r'^mission/(?P<pk>[0-9]+)/$', MissionView.as_view(), name="mission"),
    url(r'^challenge/(?P<pk>[0-9]+)/$', ChallengeView.as_view(), name="challenge"),
    url(r'^$', TemplateView.as_view(template_name="explorer/home.html"), name='home'),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]
