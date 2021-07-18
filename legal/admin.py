from django import forms
from django.contrib import admin

from legal.models import Policy
from django_summernote.admin import SummernoteModelAdmin


class PolicyForm(forms.ModelForm):
    model = Policy
    fields = '__all__'


class PolicyAdmin(SummernoteModelAdmin):
    form = PolicyForm
    list_display = ['version', 'current', 'created']
    list_editable = ['current']
    summernote_fields = ('privacy_policy', 'eula')


admin.site.register(Policy, PolicyAdmin)
