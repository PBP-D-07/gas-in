import json
import os
import uuid
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from apps.forumModule.forms import PostForm
from apps.forumModule.models import Post
from django.http import Http404, HttpResponseRedirect, JsonResponse
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

def show_post(request, post_id):
    post = None
    is_owner = False  

    try:
        uuid.UUID(post_id)
        post = get_object_or_404(Post, pk=post_id)

        if request.user.is_authenticated and post.owner == request.user:
            is_owner = True

    except (ValueError, TypeError):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'forum.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if str(item.get('id')) == post_id:
                        post = item
                        break
        except FileNotFoundError:
            pass

    if not post:
        raise Http404("Post not found")

    context = {
        'post': post if isinstance(post, Post) else None,
        'json_post': post if isinstance(post, dict) else None,
        'is_owner': is_owner, 
    }

    post_id_value = None
    if isinstance(post, Post):
        post_id_value = str(post.id)
    elif isinstance(post, dict):
        post_id_value = str(post.get("id", ""))

    context["post_id"] = post_id_value

    return render(request, 'post_detail.html', context)


@login_required
@require_http_methods(["POST"])
def create_post(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.owner = request.user
        
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

    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()

        # Kalau request dari fetch() (AJAX)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"message": "Post updated successfully"})
        
        return redirect("forumModule:show_main")
    
    # Kalau form invalid
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"error": form.errors}, status=400)

    return JsonResponse({"error": "Invalid form"}, status=400)

@login_required
@require_http_methods(["POST"])
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id, owner=request.user)
    post.delete()
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"message": "Post deleted successfully"})
    
    return HttpResponseRedirect(reverse("forumModule:show_main"))


def show_json(request):
    posts = Post.objects.select_related('owner').order_by('-created_at')
    db_data = [
        {
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
        for post in posts
    ]

    file_path = os.path.join(settings.BASE_DIR, 'data', 'forum.json')
    file_data = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
    except FileNotFoundError:
        file_data = []
    except json.JSONDecodeError:
        file_data = []

    combined_data = {
        'from_database': db_data,
        'from_file': file_data,
    }
    combined_data = db_data + file_data
    return JsonResponse(combined_data, safe=False)

def show_json_by_id(request, post_id):
    post = None

    # 1️⃣ Coba ambil dari database dulu (handle UUID dan integer)
    try:
        # Kalau post_id valid UUID
        try:
            uuid.UUID(post_id)
            post = Post.objects.select_related('owner').get(pk=post_id)
        except ValueError:
            # Kalau bukan UUID, coba pakai integer
            try:
                post = Post.objects.select_related('owner').get(pk=int(post_id))
            except (ValueError, TypeError, Post.DoesNotExist):
                post = None

        if post:
            data = {
                "id": str(post.id),
                "description": post.description,
                "thumbnail": post.thumbnail,
                "category": post.category,
                "post_views": post.post_views,
                "is_hot": post.is_post_hot,
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "owner_id": post.owner.id if post.owner else None,
                "owner_username": post.owner.username if post.owner else None,
            }
            return JsonResponse(data)
    except Exception:
        pass

    # 2️⃣ Kalau gak ada di DB, coba cek di file forum.json
    file_path = os.path.join(settings.BASE_DIR, 'data', 'forum.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if str(item.get('id')) == str(post_id):
                    return JsonResponse(item)
    except FileNotFoundError:
        pass

    # 3️⃣ Kalau gak ketemu juga
    raise Http404("Post not found")
