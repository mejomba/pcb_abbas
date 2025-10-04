from django.contrib import admin
from aaa.models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "phone", "email", "date_joined", "first_name", 'last_name')

    def get_queryset(self, request):
        return CustomUser.objects.all()

