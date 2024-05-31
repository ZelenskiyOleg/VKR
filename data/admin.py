from django.contrib import admin

from data.models import Data, Journal

# class JournalAdmin(admin.ModelAdmin):
#     list_filter = ()

admin.site.register(Data)
admin.site.register(Journal)
