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

from core.views import frontend_admin_dashboard, admin_toggle_user_status, admin_delete_job, privacy_policy, terms_of_service, help_center, admin_toggle_employer_verification, export_platform_data_csv, admin_hero_settings, admin_trusted_companies, admin_delete_trusted_company
from blog.admin_views import admin_blog_dashboard, admin_create_post, admin_edit_post, admin_delete_post, admin_blog_categories, admin_delete_category
from subscriptions.admin_views import admin_ads_dashboard, admin_ads_approve, admin_ads_reject
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, JobSitemap, BlogSitemap
from django.http import HttpResponse

sitemaps = {
    'static': StaticViewSitemap,
    'jobs': JobSitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', lambda r: HttpResponse("User-agent: *\nDisallow:\n\nSitemap: " + r.build_absolute_uri('/sitemap.xml'), content_type="text/plain")),
    path('admin/', admin.site.urls),
    path('platform-admin/', frontend_admin_dashboard, name='frontend_admin'),
    path('platform-admin/hero-settings/', admin_hero_settings, name='admin_hero_settings'),
    path('platform-admin/trusted-companies/', admin_trusted_companies, name='admin_trusted_companies'),
    path('platform-admin/trusted-companies/<int:company_id>/delete/', admin_delete_trusted_company, name='admin_delete_trusted_company'),
    path('platform-admin/export/csv/', export_platform_data_csv, name='export_platform_data_csv'),
    path('platform-admin/user/<int:user_id>/toggle/', admin_toggle_user_status, name='admin_toggle_user_status'),
    path('platform-admin/employer/<int:profile_id>/toggle-verification/', admin_toggle_employer_verification, name='admin_toggle_employer_verification'),
    path('platform-admin/job/<int:job_id>/delete/', admin_delete_job, name='admin_delete_job'),
    
    # Blog Admin
    path('platform-admin/blog/', include([
        path('', admin_blog_dashboard, name='admin_blog_dashboard'),
        path('create/', admin_create_post, name='admin_create_post'),
        path('<int:post_id>/edit/', admin_edit_post, name='admin_edit_post'),
        path('<int:post_id>/delete/', admin_delete_post, name='admin_delete_post'),
        path('categories/', admin_blog_categories, name='admin_blog_categories'),
        path('categories/<int:category_id>/delete/', admin_delete_category, name='admin_delete_category'),
    ])),
    # Ads Admin
    path('platform-admin/ads/', include([
        path('', admin_ads_dashboard, name='admin_ads_dashboard'),
        path('<int:booking_id>/approve/', admin_ads_approve, name='admin_ads_approve'),
        path('<int:booking_id>/reject/', admin_ads_reject, name='admin_ads_reject'),
    ])),
    path('privacy/', privacy_policy, name='privacy'),
    path('terms/', terms_of_service, name='terms'),
    path('help/', help_center, name='help'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('blog/', include('blog.urls')),
    path('', include('jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
