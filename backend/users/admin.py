from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('role', 'status', 'password')
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'role', 'status')
    list_editable = ('role', 'status')
    list_filter = ('role', 'status')
    search_fields = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ('subscriber', 'author')
