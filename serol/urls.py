from django.conf import settings
from django.urls import include, re_path, path
from django.contrib import admin
from django.contrib.auth import urls as django_auth_urls
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.contrib.flatpages.views import flatpage
from django.contrib.staticfiles import views
from django.conf.urls.static import static
from django.views.generic import TemplateView

from rest_framework.authtoken.views import obtain_auth_token
from django_registration.backends.activation.views import RegistrationView, ActivationView

from status.views import ScheduleView, StatusView, SerolUserForm, AllImages, RemoveMessages, \
    UpdateBadge
from explorer.views import MissionView, MissionListView, ChallengeRedirectView, \
    ChallengeView, AnalyseView, ChallengeSummary, ChallengeRetry, NextChallengeView, \
    MissionComplete, home, ChallengeRedo
from explorer.serializers import FactsView
from stickers.views import StickerView
from highscore.views import HighScoreView, AddHighScoreView
from notify.views import feedback_send


urlpatterns = [
    path('feedback/', feedback_send, name='feedback'),
    path('demo/', TemplateView.as_view(template_name='explorer/demo.html')),
    path('about/', flatpage, {'url': '/about/'}, name='about'),
    path('videos/', flatpage, {'url': '/videos/'}, name='videos'),
    path('join/', flatpage, {'url': '/join/'}, name='join'),
    path('game/', flatpage, {'url': '/game/'}, name='game'),
    path('network/',TemplateView.as_view(template_name='explorer/network.html'),{'static_url': settings.STATIC_URL}),
    path('resources/', flatpage, {'url': '/resources/'}, name='resources'),
    path('resources/workshops/', flatpage, {'url': '/resources/workshops/'}, name='workshops'),
    path('getting-started/', flatpage, {'url' : '/getting-started/'}, name='getting-started'),
    path('finish-line/', TemplateView.as_view(template_name='explorer/project_complete.html'), name="project-complete"),
    path('mission/<int:pk>/', MissionView.as_view(), name="mission"),
    path('mission/<int:mission_num>/next/', NextChallengeView.as_view(), name="challenge-next"),
    path('mission/<int:pk>/complete/', MissionComplete.as_view(), name="mission-complete"),
    path('missions/', MissionListView.as_view(), name="missions"),
    path('challenge/<int:pk>/start/', ChallengeView.as_view(), {'mode':'start'}, name="start"),
    path('challenge/<int:pk>/observe/', ChallengeView.as_view(), {'mode':'observe'}, name="observe"),
    path('challenge/<int:pk>/identify/', ChallengeView.as_view(), {'mode':'identify'}, name="identify"),
    path('challenge/<int:pk>/analyse/', AnalyseView.as_view(), name="analyse"),
    path('challenge/<int:pk>/investigate/', ChallengeView.as_view(), {'mode':'investigate'}, name="investigate"),
    path('challenge/<int:pk>/submitted/', ChallengeView.as_view(), {'mode':'submitted'}, name="submitted"),
    path('challenge/<int:pk>/summary/', ChallengeSummary.as_view(), {'mode':'summary'}, name="summary"),
    path('challenge/<int:pk>/failed/', ChallengeView.as_view(), {'mode':'failed'}, name="failed"),
    path('challenge/<int:pk>/redo/', ChallengeView.as_view(), {'mode':'redo'}, name="redo"),
    path('challenge/<int:pk>/redo/submit/', ChallengeRedo.as_view(), name="redo-submit"),
    path('challenge/<int:pk>/retry/', ChallengeRetry.as_view(), name="retry"),
    path('challenge/<int:pk>/', ChallengeRedirectView.as_view(), name="challenge"),
    path('stickers/', StickerView.as_view(), name='stickers'),
    path('images/',AllImages.as_view(), name='allimages'),
    path('api/status/<int:progressid>/<int:requestid>/', StatusView.as_view(), name="status"),
    path('api/badge/<int:progressid>/', UpdateBadge.as_view(), name="badge-update"),
    path('api/facts/',FactsView.as_view(), name="facts"),
    path('api/schedule/', ScheduleView.as_view(), name='schedule'),
    path('api/highscore/add/', AddHighScoreView.as_view() , name='highscore-add'),
    path('api/highscore/leaders/', HighScoreView.as_view()),
    path('api/messages/remove/', RemoveMessages.as_view(), name="remove-messages"),
    path('api-auth-token/', obtain_auth_token),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='explorer/login.html'), name='auth_login'),
    path('logout/', LogoutView.as_view(template_name= 'explorer/logout.html'), name='auth_logout'),
    path('accounts/register/',RegistrationView.as_view(form_class=SerolUserForm), name='registration_register'),
    # path('accounts/activate/complete/',
    #     TemplateView.as_view(
    #         template_name='django_registration/activation_complete.html'),
    #         name='django_registration_activation_complete'),
    # path('accounts/activate/<slug:activation_key>',
    #     ActivationView.as_view(),
    #     name='registration_activate'),
    # path('accounts/register/complete/',
    #     TemplateView.as_view(
    #         template_name='django_registration/registration_complete.html'),
    #         name='django_registration_complete'),

    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
      html_email_template_name='registration/password_reset_email.html'
    )),
    path('accounts/',
        include('django_registration.backends.activation.urls')
    ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),
    re_path(r'^(?P<url>.*/)$', flatpage),
]

if settings.DEBUG:

    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += (
            path('500/', TemplateView.as_view(template_name='500.html'), name="error500"),
            path('404/', TemplateView.as_view(template_name='404.html'), name="error404")
            )
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
