from django.contrib import admin
from terms.models import Agreement, Terms

class TermsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Terms, TermsAdmin)
