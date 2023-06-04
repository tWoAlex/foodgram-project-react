from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('email', 'role', 'first_name', 'last_name')
    list_display = ('username', 'email', 'role', 'first_name', 'last_name')
    list_editable = ('role',)
    list_filter = ('role',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
