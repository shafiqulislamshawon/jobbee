from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django_countries.fields import CountryField
from simple_history.models import HistoricalRecords

class User(AbstractUser):
    is_employer = models.BooleanField(default=False)
    is_seeker = models.BooleanField(default=False)
    history = HistoricalRecords()

class EmployerProfile(models.Model):
    COMPANY_SIZE_CHOICES = (
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    )
    VERIFICATION_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_banner = models.ImageField(upload_to='company_banners/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, blank=True)
    credits = models.IntegerField(default=0)
    history = HistoricalRecords()
    
    @property
    def reputation_score(self):
        score = 50 # Base score
        if self.is_verified:
            score += 20
        
        reviews = self.reviews.all()
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            score += (avg_rating / 5.0) * 15
        
        if self.user.jobs.count() > 0:
            score += 5
            
        from jobs.models import Application
        hired_count = Application.objects.filter(job__employer=self.user, status='OFFER').count()
        if hired_count > 0:
            score += 10
            
        return min(int(score), 100)
    
    def __str__(self):
        return self.company_name

class SeekerProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    )
    AGE_CHOICES = (
        ('18-24', '18-24'),
        ('25-34', '25-34'),
        ('35-44', '35-44'),
        ('45-54', '45-54'),
        ('55+', '55+'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seeker_profile')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, help_text='Comma-separated skills', db_index=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    age_group = models.CharField(max_length=10, choices=AGE_CHOICES, blank=True, null=True)
    resume_score = models.PositiveIntegerField(null=True, blank=True)
    missing_skills = models.TextField(blank=True)
    resume_suggestions = models.TextField(blank=True)
    location = CountryField(blank=True, blank_label='(select country)', db_index=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return f'{self.user.username} Profile'

class Education(models.Model):
    seeker = models.ForeignKey(SeekerProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Experience(models.Model):
    seeker = models.ForeignKey(SeekerProfile, on_delete=models.CASCADE, related_name='experience')
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"

class Certification(models.Model):
    seeker = models.ForeignKey(SeekerProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    issue_date = models.DateField()
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class CompanyPhoto(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='company_photos/')
    caption = models.CharField(max_length=255, blank=True)

class CompanyReview(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} stars by {self.reviewer.username}"

class Referral(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('REGISTERED', 'Registered'),
        ('REWARDED', 'Rewarded')
    )
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    referred_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} -> {self.referred_email} ({self.status})"

class RecruiterSeat(models.Model):
    employer_profile = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='recruiter_seats')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_seat_profile')
    invited_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} at {self.employer_profile.company_name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}"
