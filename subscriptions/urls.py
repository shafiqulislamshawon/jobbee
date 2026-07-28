from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('process-checkout/<int:plan_id>/', views.process_checkout, name='process_checkout'),
    path('addons/', views.addons_store, name='addons_store'),
    path('addons/<int:addon_id>/checkout/', views.checkout_addon, name='checkout_addon'),
    path('addons/<int:addon_id>/process/', views.process_addon_checkout, name='process_addon_checkout'),
    path('billing/', views.billing_dashboard, name='billing_dashboard'),
    path('billing/invoice/', views.download_invoice, name='download_invoice'),
    path('ads/', views.ad_spaces, name='ad_spaces'),
    path('ads/<int:space_id>/book/', views.ad_book, name='ad_book'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
]
