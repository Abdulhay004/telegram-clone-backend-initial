from django.contrib import admin

from .models import User, DeviceInfo, Contact

admin.site.register(User)
admin.site.register(Contact)
