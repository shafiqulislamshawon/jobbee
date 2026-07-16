from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from jobs.models import Job
from blog.models import Post

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'subscriptions:pricing', 'privacy', 'terms', 'help', 'blog_home', 'job_list']

    def location(self, item):
        return reverse(item)

class JobSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Job.objects.filter(is_active=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at
        
    def location(self, obj):
        return reverse('job_detail', args=[obj.id])

class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Post.objects.filter(status='PUBLISHED').order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at
        
    def location(self, obj):
        return reverse('post_detail', args=[obj.slug])
