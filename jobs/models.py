from django.db import models
from accounts.models import User

class Job(models.Model):
    EMPLOYMENT_TYPES = (
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERNSHIP', 'Internship'),
    )
    REMOTE_STATUS = (
        ('REMOTE', 'Remote'),
        ('HYBRID', 'Hybrid'),
        ('ON_SITE', 'On-site'),
    )
    CURRENCY_CHOICES = (
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('INR', 'Indian Rupee (₹)'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    salary_min = models.PositiveIntegerField(blank=True, null=True)
    salary_max = models.PositiveIntegerField(blank=True, null=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='FULL_TIME')
    remote_status = models.CharField(max_length=20, choices=REMOTE_STATUS, default='ON_SITE')
    
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    location = models.CharField(max_length=255, blank=True)
    benefits = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True, help_text='Comma-separated skills')
    experience = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    
    deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def currency_symbol(self):
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'CAD': 'C$',
            'AUD': 'A$',
            'INR': '₹'
        }
        return symbols.get(self.currency, '$')

class Application(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('REVIEWED', 'Reviewed'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'),
        ('REJECTED', 'Rejected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f'{self.applicant.username} - {self.job.title}'

class JobEngagement(models.Model):
    ACTION_CHOICES = (
        ('VIEW', 'View'),
        ('CLICK', 'Click'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='engagements')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_engagements')
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES, default='VIEW')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action_type} on {self.job.title}"
