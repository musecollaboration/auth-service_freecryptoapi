from django.contrib import admin
from apps.accounts.models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'account_type')
    ordering = ('email',)

    def has_add_permission(self, request):
        return request.user.is_superuser  # Только суперпользователи могут добавлять


    def has_change_permission(self, request, obj=None):
        return request.user.is_staff  # Разрешаем редактировать только админам


    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Ограничиваем удаление только суперпользователям
