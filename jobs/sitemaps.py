from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Job
from accounts.models import EmployerProfile

class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Job.objects.filter(is_active=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('job_detail', args=[obj.id])

class CompanySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return EmployerProfile.objects.all().order_by('id')

    def location(self, obj):
        return reverse('company_detail', args=[obj.id])
