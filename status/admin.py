from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.auth.admin import UserAdmin

from status.models import User

class CustomUserAdmin(UserAdmin):


    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', )}),
        (_('Tokens'), {'fields' :('token', 'archive_token')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, CustomUserAdmin)
