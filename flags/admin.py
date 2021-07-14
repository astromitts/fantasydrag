from django.contrib import admin
from django import forms
from flags.models import FeatureFlag


class FeatureFlagForm(forms.ModelForm):
    fields = '__all__'
    form = FeatureFlag


class FeatureFlagAdmin(admin.ModelAdmin):
    form = FeatureFlagForm
    list_display = ['title', 'value', 'changed']
    list_editable = ['value', ]

admin.site.register(FeatureFlag, FeatureFlagAdmin)
