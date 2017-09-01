from django.contrib import admin

from explorer.models import *
from status.models import *


class MissionAdmin(admin.ModelAdmin):
    list_display = ('name','number')

class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name','number','mission')

admin.site.register(Mission, MissionAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Progress)
