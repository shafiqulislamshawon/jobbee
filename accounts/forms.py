from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SeekerProfile, EmployerProfile, Education, Experience, Certification

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('seeker', 'I am looking for a job'),
        ('employer', 'I am hiring'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email',)

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
        fields = ['resume', 'portfolio_url', 'skills', 'gender', 'age_group']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'skills': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md', 'placeholder': 'e.g., Python, Django, React'}),
            'gender': forms.Select(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
            'age_group': forms.Select(attrs={'class': 'shadow-sm focus:ring-accent focus:border-accent block w-full sm:text-sm border-gray-300 rounded-md'}),
        }

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
