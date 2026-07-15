from django.contrib import admin
from .models import Plan, EmployerSubscription, Transaction, AddOn, EmployerAddOn
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'job_limit', 'duration_days')
    # list_filter = ('is_active',)

@admin.register(EmployerSubscription)
class EmployerSubscriptionAdmin(SimpleHistoryAdmin):
    list_display = ('employer', 'plan', 'status', 'start_date', 'end_date')
    list_filter = ('status',)

@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin):
    list_display = ('subscription', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
