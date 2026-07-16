from django import forms
from .models import Post, Category
from django.utils.text import slugify

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'status', 'featured_image', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4'}),
            'status': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4'}),
            'featured_image': forms.FileInput(attrs={'class': 'w-full'}),
            'content': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4', 'id': 'blog-content-editor'}),
        }

class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance
