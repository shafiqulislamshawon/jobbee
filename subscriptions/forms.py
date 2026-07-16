from django import forms
from .models import AdBooking

class AdBookingForm(forms.ModelForm):
    class Meta:
        model = AdBooking
        fields = ['image', 'target_url', 'start_date', 'end_date']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4'}),
            'target_url': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4'}),
        }
