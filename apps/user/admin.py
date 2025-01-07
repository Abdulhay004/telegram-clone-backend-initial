from django.contrib import admin

from .models import User, DeviceInfo, Contact, NotificationPreference

# admin.site.register(User)
# admin.site.register(Contact)
admin.site.register(NotificationPreference)