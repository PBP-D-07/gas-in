import json
import os
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from apps.forumModule.forms import PostForm
from apps.forumModule.models import Post
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

def show_main(request):
    filter_type = request.GET.get("filter", "all")

    if filter_type == "all":
        post_list = Post.objects.all().order_by('-created_at')
    else:
        post_list = Post.objects.filter(owner=request.user).order_by('-created_at')

    context = {
        'name': request.user.username if request.user.is_authenticated else 'Guest',
        'post_list': post_list,
    }

    return render(request, "forumMain.html", context)


def show_post(request, id):
    post = get_object_or_404(Post, pk=id)
    post.increment_views() 
    
    context = {
        'post': post,
        'comments': post.comments.all().order_by('-created_at')
    }
    return render(request, 'post_detail.html', context)

@login_required
@require_http_methods(["POST"])
def create_post(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.owner = request.user
        
        # Handle thumbnail optional
        thumbnail = form.cleaned_data.get("thumbnail")
        if not thumbnail:
            post.thumbnail = None
        
        post.save()
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "message": "Post created successfully",
                "post_id": str(post.id)
            })
        return redirect("forumModule:show_main")
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": form.errors}, status=400)
        return JsonResponse({"error": "Invalid form"}, status=400)


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id, owner=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('forumModule:show_main')
    else:
        form = PostForm(instance=post)

    context = {'form': form, 'post': post}
    return render(request, "edit_post.html", context)


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id, owner=request.user)
    post.delete()
    return HttpResponseRedirect(reverse('forumModule:show_main'))

def show_json(request):
    file_path = os.path.join(settings.BASE_DIR, 'data', 'forum.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return JsonResponse({'error': 'forum.json file not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    return JsonResponse(data, safe=False)


def show_json_by_id(request, post_id):
    try:
        post = Post.objects.select_related('owner').get(pk=post_id)
        data = {
            'id': str(post.id),
            'description': post.description,
            'thumbnail': post.thumbnail,
            'category': post.category,
            'post_views': post.post_views,
            'is_hot': post.is_post_hot,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'owner_id': post.owner.id if post.owner else None,
            'owner_username': post.owner.username if post.owner else None,
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)