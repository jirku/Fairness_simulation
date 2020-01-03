from django.contrib import admin

# Register your models here.

from .models import Policy, Market, Bank, Applicant_group, Applicant

admin.site.register(Policy)
admin.site.register(Market)
admin.site.register(Bank)
admin.site.register(Applicant_group)
admin.site.register(Applicant)
