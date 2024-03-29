from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from pagedown.widgets import AdminPagedownWidget

from explorer.models import *
from status.models import *
from stickers.models import *
from highscore.models import *


class MissionAdmin(admin.ModelAdmin):
    list_display = ('name','number')

class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name','number','mission')

# Define a new FlatPageAdmin
class FlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse', ),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super(FlatPageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class FactAdmin(admin.ModelAdmin):
    list_display = ('tagline','category','published')

class BodyAdmin(admin.ModelAdmin):
    list_display = ('name','icon','active')

class StickerAdmin(admin.ModelAdmin):
    list_display = ('desc','challenge')
    ordering = ('challenge',)

admin.site.register(Mission, MissionAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Sticker, StickerAdmin)
admin.site.register(PersonSticker)
admin.site.register(Body, BodyAdmin)
admin.site.register(Score)
admin.site.register(LevelScore)
admin.site.register(Fact, FactAdmin)
admin.site.register(Season)
admin.site.register(Activity)

# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
