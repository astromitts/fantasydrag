from django.http import HttpResponse
from django.template import loader
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse

from legal.forms import PolicyForm
from legal.models import Policy, PolicyLog


class PolicyLanding(View):
    def setup(self, request, *args, **kwargs):
        super(PolicyLanding, self).setup(request, *args, **kwargs)
        self.form = PolicyForm
        self.user = request.user
        self.template = loader.get_template('pages/legal/landing.html')

    def get(self, request, *args, **kwargs):
        context = {'form': self.form()}
        return HttpResponse(self.template.render(context, request))

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            log = PolicyLog.fetch(request.user)
            log.policy = Policy.get_current()
            log.save()
            request.session['policy_pass'] = True
            return redirect(reverse('home'))
        context = {'form': self.form()}
        return HttpResponse(self.template.render(context, request))


class PolicyView(View):
    def setup(self, request, *args, **kwargs):
        super(PolicyView, self).setup(request, *args, **kwargs)
        self.current_policy = Policy.objects.get(current=True)
        self.template = loader.get_template('pages/legal/policy.html')


class PrivacyPolicy(PolicyView):
    def get(self, request, *args, **kwargs):
        context = {
            'page_title': 'Privacy Policy',
            'content': self.current_policy.privacy_policy
        }
        return HttpResponse(self.template.render(context, request))


class EULA(PolicyView):
    def get(self, request, *args, **kwargs):
        context = {
            'page_title': 'EULA',
            'content': self.current_policy.eula
        }
        return HttpResponse(self.template.render(context, request))
