from django.contrib import admin
from .models import Mention, Alert

@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'created_at', 'sentiment', 'topic', 'processed')
    search_fields = ('text', 'author')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id','alert_type','mention','created_at','resolved')
