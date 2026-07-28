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
    detail = models.CharField(max_length=255, blank=True, null=True, help_text="Short description of the plan")
    
    # Table Fields
    best_for = models.CharField(max_length=255, blank=True, null=True)
    job_posts_text = models.CharField(max_length=255, blank=True, null=True)
    applications_text = models.CharField(max_length=255, blank=True, null=True, default='Unlimited')
    cv_database_access = models.CharField(max_length=255, blank=True, null=True)
    featured_jobs_text = models.CharField(max_length=255, blank=True, null=True)
    homepage_placement = models.BooleanField(default=False)
    social_media_promotion = models.CharField(max_length=255, blank=True, null=True)
    company_branding = models.CharField(max_length=255, blank=True, null=True)
    analytics_dashboard = models.CharField(max_length=255, blank=True, null=True)
    dedicated_account_manager = models.BooleanField(default=False)
    recruitment_consultation = models.BooleanField(default=False)
    priority_customer_support = models.CharField(max_length=255, blank=True, null=True)
    remote_hybrid_support = models.BooleanField(default=False)
    custom_hiring_campaigns = models.BooleanField(default=False)
    
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

    @property
    def total_job_limit(self):
        if not self.plan or self.plan.job_limit == -1:
            return -1
        extra_jobs_count = self.employer.addons.filter(
            addon__addon_type='EXTRA_JOB',
            is_used=False
        ).aggregate(
            total_extra=models.Sum('quantity')
        )['total_extra'] or 0
        return self.plan.job_limit + extra_jobs_count

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

class AdSpace(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50, unique=True)
    width = models.PositiveIntegerField(help_text="Width in pixels")
    height = models.PositiveIntegerField(help_text="Height in pixels")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.width}x{self.height})"

class AdBooking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved & Active'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed / Expired'),
    )
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='ad_bookings')
    ad_space = models.ForeignKey(AdSpace, on_delete=models.CASCADE, related_name='bookings')
    image = models.ImageField(upload_to='ads/')
    target_url = models.URLField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ad by {self.user.username} in {self.ad_space.name}"


class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
    )
    code = models.CharField(max_length=20, unique=True, help_text="Coupon code string")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Percentage or Fixed amount depending on type")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True, help_text="Leave blank for no expiration date")
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum total number of times this coupon can be used")
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.code} - {self.discount_value} {self.discount_type}"

    def check_validity(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False, "This coupon is inactive."
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False, "This coupon has reached its maximum uses."
        if self.valid_from > now:
            return False, "This coupon is not valid yet."
        if self.valid_to and self.valid_to < now:
            return False, "This coupon has expired."
        return True, "Valid"

    def is_valid(self):
        is_valid, _ = self.check_validity()
        return is_valid

    def get_discount_amount(self, total_price):
        if self.discount_type == 'PERCENTAGE':
            return float(total_price) * (float(self.discount_value) / 100)
        return min(float(self.discount_value), float(total_price))

class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='coupon_usages')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_type = models.CharField(max_length=50, help_text="e.g. SUBSCRIPTION, ADDON, TEMPLATE")
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code} saving {self.discount_amount}"
