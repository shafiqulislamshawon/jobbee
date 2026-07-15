from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from jobs.sitemaps import JobSitemap, CompanySitemap

sitemaps = {
    'jobs': JobSitemap,
    'companies': CompanySitemap,
}

from core.views import frontend_admin_dashboard, admin_toggle_user_status, admin_delete_job, privacy_policy, terms_of_service, help_center, admin_toggle_employer_verification, export_platform_data_csv

urlpatterns = [
    path('admin/', admin.site.urls),
    path('platform-admin/', frontend_admin_dashboard, name='frontend_admin'),
    path('platform-admin/export/csv/', export_platform_data_csv, name='export_platform_data_csv'),
    path('platform-admin/user/<int:user_id>/toggle/', admin_toggle_user_status, name='admin_toggle_user_status'),
    path('platform-admin/employer/<int:profile_id>/toggle-verification/', admin_toggle_employer_verification, name='admin_toggle_employer_verification'),
    path('platform-admin/job/<int:job_id>/delete/', admin_delete_job, name='admin_delete_job'),
    path('privacy/', privacy_policy, name='privacy'),
    path('terms/', terms_of_service, name='terms'),
    path('help/', help_center, name='help'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('blog/', include('blog.urls')),
    path('', include('jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
