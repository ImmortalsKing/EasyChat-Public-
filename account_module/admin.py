from django.contrib import admin

from account_module import models

admin.site.register(models.User)
admin.site.register(models.Country)
admin.site.register(models.InvitationCode)

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug':['title']
    }