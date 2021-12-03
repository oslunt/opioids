from django.contrib import admin
from .models import Drug, Prescriber, State, Prescribercredential, Prescriberdrug
# Register your models here.

admin.site.register(Drug)
admin.site.register(Prescriber)
admin.site.register(State)
admin.site.register(Prescribercredential)
admin.site.register(Prescriberdrug)