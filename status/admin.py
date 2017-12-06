from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.auth.admin import UserAdmin

from status.models import User, Progress, Answer, Question, UserAnswer, Proposal

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'default_proposal' )}),
        (_('Tokens'), {'fields' :('token', 'archive_token')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class AnswerInline(admin.TabularInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'text')
    inlines = [AnswerInline,]


admin.site.register(User, CustomUserAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Proposal)

admin.site.site_header = 'SEROL admin'
