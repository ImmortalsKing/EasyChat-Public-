from django.contrib import admin

from chat_module import models

admin.site.register(models.Message)
admin.site.register(models.Gallery)
admin.site.register(models.UserChannel)

@admin.register(models.GalleryRoom)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','by_who','is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']

    prepopulated_fields = {
        'slug' : ['title']
    }