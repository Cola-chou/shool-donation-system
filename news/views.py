from django.shortcuts import render
from django.views.generic import DetailView
from .models import News
from apps.donation.models import DonationProject


class NewDetailView(DetailView):
    model = News
    template_name = 'new_detail.html'
    context_object_name = 'new'

    def get_context_data(self, **kwargs):
        projects = None
        context = {}
        if self.object:
            projects = DonationProject.objects.filter(project_news_id=self.object.pk)
            print(projects)
        context['projects'] = projects
        context.update(kwargs)
        return super(NewDetailView, self).get_context_data(**context)
