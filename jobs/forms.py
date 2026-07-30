from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    education = forms.MultipleChoiceField(
        choices=[
            ('High School', 'High School'),
            ('Diploma', 'Diploma'),
            ('Bachelor\'s Degree', 'Bachelor\'s Degree'),
            ('Master\'s Degree', 'Master\'s Degree'),
            ('PhD', 'PhD')
        ],
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    class Meta:
        model = Job
        fields = [
            'title', 'category', 'description', 'responsibilities', 'requirements', 'professional_qualifications',
            'salary_min', 'salary_max', 'is_salary_negotiable', 'show_salary', 'employment_type', 'remote_status', 
            'location', 'sub_location', 'anywhere_in_bd', 'benefits', 'skills', 'experience', 'education', 'deadline',
            'is_featured'
        ]
        labels = {
            'description': 'Job Context',
            'requirements': 'Additional Requirements',
            'sub_location': 'Sub-location / City',
        }
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'title': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm', 'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm', 'rows': 4}),
            'professional_qualifications': forms.Textarea(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm', 'rows': 3}),
            'sub_location': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        self.subscription = kwargs.pop('subscription', None)
        super(JobForm, self).__init__(*args, **kwargs)
        if not self.subscription or not self.subscription.is_active():
            self.fields.pop('is_featured', None)
        elif not self.subscription.plan.can_feature_jobs:
            has_featured_token = self.subscription.employer.addons.filter(addon__addon_type='FEATURED_JOB', is_used=False).exists()
            if not has_featured_token:
                self.fields.pop('is_featured', None)

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        is_salary_negotiable = cleaned_data.get('is_salary_negotiable')
        
        if not is_salary_negotiable:
            if not salary_min:
                self.add_error('salary_min', 'Minimum salary is required if not negotiable.')
            if not salary_max:
                self.add_error('salary_max', 'Maximum salary is required if not negotiable.')
                
        if salary_min and salary_max and salary_min > salary_max:
            self.add_error('salary_max', 'Maximum salary cannot be less than minimum salary.')
            
        education_list = cleaned_data.get('education')
        if education_list and isinstance(education_list, list):
            cleaned_data['education'] = ', '.join(education_list)
            
        return cleaned_data
