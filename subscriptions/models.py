from django.db import models
from accounts.models import EmployerProfile
from simple_history.models import HistoricalRecords

class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    job_limit = models.IntegerField(help_text="Number of jobs allowed (-1 for unlimited)", default=1)
    duration_days = models.PositiveIntegerField(default=30)
    has_banner = models.BooleanField(default=False)
    can_feature_jobs = models.BooleanField(default=False)
    has_verification_badge = models.BooleanField(default=False)
    has_advanced_matching = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class EmployerSubscription(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('PENDING', 'Pending Approval'),
    )
    employer = models.OneToOneField(EmployerProfile, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    jobs_posted = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    history = HistoricalRecords()
    
    def is_active(self):
        from django.utils import timezone
        return self.status == 'ACTIVE' and self.end_date >= timezone.now()
        
    def __str__(self):
        return f"{self.employer.company_name} - {self.plan.name}"

    def can_post_job(self):
        if not self.is_active():
            return False
        if self.plan.job_limit == -1: # Unlimited
            return True
        if self.jobs_posted < self.plan.job_limit:
            return True
            
        extra_jobs_count = self.employer.addons.filter(
            addon__addon_type='EXTRA_JOB',
            is_used=False
        ).count()
        return extra_jobs_count > 0

    def __str__(self):
        return f"{self.employer.company_name} - {self.plan.name if self.plan else 'No Plan'}"

class Transaction(models.Model):
    subscription = models.ForeignKey(EmployerSubscription, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='COMPLETED')
    history = HistoricalRecords()

    def __str__(self):
        return f"Transaction {self.id} for {self.subscription.employer.company_name}"


class AddOn(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    addon_type = models.CharField(max_length=50, help_text="e.g., FEATURED_JOB, EXTRA_JOB") 
    
    def __str__(self):
        return self.name


class EmployerAddOn(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='addons')
    addon = models.ForeignKey(AddOn, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    purchased_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.addon.name} for {self.employer.company_name}"
