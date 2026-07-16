from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Post, Category
from .forms import BlogPostForm, BlogCategoryForm
from django.utils.text import slugify

@user_passes_test(lambda u: u.is_staff)
def admin_blog_dashboard(request):
    posts = Post.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'core/admin_blog_dashboard.html', {
        'posts': posts,
        'categories': categories
    })

@user_passes_test(lambda u: u.is_staff)
def admin_create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_blog_dashboard')
    else:
        form = BlogPostForm()
    return render(request, 'core/admin_blog_form.html', {'form': form, 'is_edit': False})

@user_passes_test(lambda u: u.is_staff)
def admin_edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.slug = slugify(post.title)
            post.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('admin_blog_dashboard')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'core/admin_blog_form.html', {'form': form, 'is_edit': True, 'post': post})

@user_passes_test(lambda u: u.is_staff)
def admin_delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        messages.success(request, 'Blog post deleted successfully!')
    return redirect('admin_blog_dashboard')

@user_passes_test(lambda u: u.is_staff)
def admin_blog_categories(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('admin_blog_categories')
    else:
        form = BlogCategoryForm()
    return render(request, 'core/admin_blog_categories.html', {'categories': categories, 'form': form})

@user_passes_test(lambda u: u.is_staff)
def admin_delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    return redirect('admin_blog_categories')
