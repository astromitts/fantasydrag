from django import forms
from django.contrib import admin

from messagecenter.models import ContactMessage
from django_summernote.admin import SummernoteModelAdmin


class ContactMessageForm(forms.ModelForm):
    model = ContactMessage
    fields = '__all__'


class ContactMessageAdmin(SummernoteModelAdmin):
    form = ContactMessageForm
    list_display = ['from_user', 'message_type', 'time_sent', 'status']
    list_editable = ['status']
    summernote_fields = ('content',)


admin.site.register(ContactMessage, ContactMessageAdmin)
