from django.contrib import admin
from .models import UserAccount, AccountData

admin.site.register(UserAccount)
admin.site.register(AccountData)