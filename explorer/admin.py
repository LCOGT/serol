from django.contrib import admin

from explorer.models import *
from status.models import *

admin.site.register(Mission)
admin.site.register(Challenge)
admin.site.register(Target)
admin.site.register(Progress)
