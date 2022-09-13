from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages

from status.models import User, Progress, Answer, Question, UserAnswer, Proposal, Progress
from notify.views import send_notifications


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer

class UserChallenges(admin.TabularInline):
    model = Progress

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'default_proposal', 'mission_1', 'mission_2', 'mission_3' )}),
        (_('Tokens'), {'fields' :('token', 'archive_token')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [UserChallenges, UserAnswerInline,]

class AnswerInline(admin.TabularInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'text')
    inlines = [AnswerInline,]

def remove_images(modeladmin, request, queryset):
    queryset.update(image_file=None, image_status=0)
remove_images.short_description = "Remove images"

def resend_email(modeladmin, request, queryset):
    queryset = queryset.filter(status__in=['Summary','Analyse','Identify'])
    if queryset:
        send_notifications(queryset)
        messages.success(request, "ReSend {} emails".format(queryset.count()))
    else:
        messages.error(request, "No valid Progress")
resend_email.short_description = 'Resend email'

class ProgressAdmin(admin.ModelAdmin):
    list_filter = ( 'status', 'challenge__number','challenge__mission__number')
    list_display = ('user','target','challenge','coloured_state','last_update', 'ra','dec','has_image')
    fields = ['user','challenge', 'target', 'requestgroup', 'requestid', 'frameids', 'status', 'last_update', 'image_file', 'image_tag', 'image_status', 'ra','dec','siteid']
    readonly_fields = ['image_tag']
    actions = [remove_images, resend_email]

admin.site.register(User, CustomUserAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Proposal)
admin.site.register(Progress, ProgressAdmin)

admin.site.site_header = 'SEROL admin'
