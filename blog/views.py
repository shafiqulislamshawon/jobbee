from django.shortcuts import render, get_object_or_404
from .models import Post, Category

def post_list(request):
    posts = Post.objects.filter(status='PUBLISHED').order_by('-created_at')
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
        
    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'categories': categories,
        'current_category': category_slug
    })

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='PUBLISHED')
    return render(request, 'blog/post_detail.html', {'post': post})
