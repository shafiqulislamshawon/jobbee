from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SeekerProfile, EmployerProfile, Education, Experience, Certification, Reference

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('seeker', 'I am looking for a job'),
        ('employer', 'I am hiring'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add required attribute to email
        self.fields['email'].required = True
        
        for field_name, field in self.fields.items():
            if field_name != 'role':
                # Base Tailwind classes for premium input styling
                base_classes = (
                    'appearance-none block w-full px-4 py-3 '
                    'bg-gray-50 border border-gray-200 text-gray-900 rounded-lg '
                    'focus:bg-white focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent '
                    'transition-all duration-200 ease-in-out sm:text-sm'
                )
                
                # Add validation attributes
                attrs = {'class': base_classes, 'required': 'required'}
                
                if field_name == 'username':
                    attrs['minlength'] = '3'
                    attrs['placeholder'] = 'Choose a username'
                elif field_name == 'email':
                    attrs['type'] = 'email'
                    attrs['placeholder'] = 'you@example.com'
                elif 'password' in field_name:
                    attrs['minlength'] = '8'
                    attrs['placeholder'] = '••••••••'
                    
                field.widget.attrs.update(attrs)


    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        if role == 'employer':
            user.is_employer = True
        elif role == 'seeker':
            user.is_seeker = True
            
        if commit:
            user.save()
            if role == 'employer':
                EmployerProfile.objects.create(user=user, company_name=user.username)
            elif role == 'seeker':
                SeekerProfile.objects.create(user=user)
        return user

class SeekerProfileForm(forms.ModelForm):
    class Meta:
        model = SeekerProfile
        fields = ['profile_picture', 'full_name', 'phone_number', 'address', 'portfolio_url', 'github_url', 'linkedin_url', 'twitter_url', 'career_summary', 'skills', 'languages', 'extracurricular_activities', 'gender', 'age_group']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'career_summary': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 4}),
            'extracurricular_activities': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3, 'placeholder': 'e.g., Volunteer work, clubs, side projects'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'github_url': forms.URLInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'twitter_url': forms.URLInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'skills': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md', 'placeholder': 'e.g., Python, Django, React'}),
            'languages': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md', 'placeholder': 'e.g., English, Bengali, Spanish'}),
            'gender': forms.Select(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'age_group': forms.Select(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
        }

class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ('name', 'relationship', 'company', 'contact_info')

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'logo', 'company_banner', 'website', 'description']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'website': forms.URLInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'logo': forms.FileInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'company_banner': forms.FileInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ('institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'description')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ('job_title', 'company', 'start_date', 'end_date', 'is_current', 'description')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ('name', 'issuer', 'issue_date', 'url')
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }
