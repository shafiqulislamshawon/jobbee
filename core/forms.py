from django import forms
from .models import HeroSectionSettings, TrustedCompany

class HeroSectionSettingsForm(forms.ModelForm):
    class Meta:
        model = HeroSectionSettings
        fields = '__all__'
        widgets = {
            'badge_text': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'heading_line_1': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'heading_line_2_colored': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'subheading': forms.Textarea(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm', 'rows': 3}),
            'companies_section_title': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'search_placeholder_1': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'search_placeholder_2': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'search_button_text': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'popular_tags': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            
            'card_1_number': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'card_1_label': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'card_2_title': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'card_2_tag_1': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'card_2_tag_2': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'card_3_number': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'card_3_label': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'card_4_number': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'card_4_label': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
        }

class TrustedCompanyForm(forms.ModelForm):
    class Meta:
        model = TrustedCompany
        fields = ['name', 'logo', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'order': forms.NumberInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
        }

from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'
        widgets = {
            'quote': forms.Textarea(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm', 'rows': 4}),
            'author_name': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'author_title': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'author_avatar': forms.ClearableFileInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'badge_initial': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm', 'maxlength': '5'}),
            'hired_role': forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-accent focus:ring-accent sm:text-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-accent focus:ring-accent'}),
        }
