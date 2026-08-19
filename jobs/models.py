from django.db import models
from accounts.models import User
from django_countries.fields import CountryField
from simple_history.models import HistoricalRecords

class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class name (e.g. from FontAwesome or similar)')

    class Meta:
        verbose_name_plural = 'Job Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Job(models.Model):
    EMPLOYMENT_TYPES = (
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contractual'),
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
        ('BDT', 'Bangladeshi Taka (৳)'),
    )

    title = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    salary_min = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    salary_max = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    is_salary_negotiable = models.BooleanField(default=False)
    show_salary = models.BooleanField(default=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='FULL_TIME', db_index=True)
    remote_status = models.CharField(max_length=20, choices=REMOTE_STATUS, default='ON_SITE', db_index=True)
    
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    location = CountryField(blank=True, blank_label='(select country)', db_index=True)
    sub_location = models.CharField(max_length=255, blank=True)
    anywhere_in_bd = models.BooleanField(default=False, verbose_name="Anywhere in Bangladesh")
    benefits = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True, help_text='Comma-separated skills')
    experience = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=255, blank=True)
    professional_qualifications = models.TextField(blank=True)
    
    deadline = models.DateField(blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    history = HistoricalRecords()
    is_active = models.BooleanField(default=True, db_index=True)
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, db_index=True)

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
            'INR': '₹',
            'BDT': '৳'
        }
        return symbols.get(self.currency, '$')

class Application(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('REVIEWED', 'Reviewed'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW', 'Interview Scheduled'),
        ('OFFER', 'Offer Extended'),
        ('REJECTED', 'Rejected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications', db_index=True)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', db_index=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    applied_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    match_score = models.PositiveIntegerField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"

class SavedCandidate(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_candidates')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_by_employers')
    notes = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employer', 'seeker')

    def __str__(self):
        return f"{self.employer.username} saved {self.seeker.username}"

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

class SavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    query = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username}: {self.query} in {self.location}"

class Assessment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class AssessmentResult(models.Model):
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField()
    taken_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('seeker', 'assessment')
        
    def __str__(self):
        return f"{self.seeker.username} - {self.assessment.name} ({self.score}%)"
