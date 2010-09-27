from django.contrib import admin
from terms.models import Agreement, Terms
from django.contrib.comments.views.moderation import perform_flag, perform_approve, perform_delete

class TermsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Terms, TermsAdmin)
