import json, os, uuid, requests
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from apps.forumModule.forms import PostForm
from apps.forumModule.models import Post, Comment
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def update_post_flutter(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    if post.owner != request.user:
        return JsonResponse({"error": "Forbidden"}, status=403)

    data = json.loads(request.body)

    post.description = data.get("description", post.description)
    post.thumbnail = data.get("thumbnail", post.thumbnail)
    post.save()

    return JsonResponse({
        "success": True,
        "message": "Post updated successfully"
    })


@csrf_exempt
@login_required
def delete_post_flutter(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    post = get_object_or_404(Post, id=post_id)

    # 🔒 hanya owner yg boleh delete
    if post.owner != request.user:
        return JsonResponse(
            {"error": "You are not allowed to delete this post"},
            status=403
        )

    post.delete()
    return JsonResponse({"status": "success"})

@csrf_exempt
def increment_view_flutter(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.post_views += 1
    post.save()

    return JsonResponse({
        'status': 'ok',
        'views': post.post_views
    })

def check_like_flutter(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'liked': False,
            'like_count': 0,
        })

    post = get_object_or_404(Post, pk=post_id)
    return JsonResponse({
        'liked': request.user in post.likes.all(),
        'like_count': post.likes.count(),
    })

@csrf_exempt
def toggle_like_flutter(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'Authentication required'
        }, status=401)

    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count(),
    })


@csrf_exempt
def create_post_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        description = strip_tags(data.get("description", ""))
        category = data.get("category", "")
        thumbnail = data.get("thumbnail", "")
        user = request.user

        # Validasi kategori agar sesuai pilihan model
        valid_categories = dict(Post.CATEGORY_CHOICES).keys()
        if category not in valid_categories:
            return JsonResponse({"status": "error", "message": "Invalid category"}, status=400)

        new_post = Post.objects.create(
            description=description,
            category=category,
            thumbnail=thumbnail if thumbnail else None,
            owner=user,
        )

        return JsonResponse({"status": "success", "post_id": str(new_post.id)}, status=200)

    return JsonResponse({"status": "error"}, status=405)


def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)

@csrf_exempt
@require_POST
def add_post_entry_ajax(request):
    description = strip_tags(request.POST.get("description"))
    category = request.POST.get("category")
    thumbnail = request.POST.get("thumbnail")
    user = request.user

    if not description or not category:
        return JsonResponse({'error': 'Description and category are required'}, status=400)

    valid_categories = dict(Post.CATEGORY_CHOICES).keys()
    if category not in valid_categories:
        return JsonResponse({"error": "Invalid category"}, status=400)

    new_post = Post.objects.create(
        description=description,
        category=category,
        thumbnail=thumbnail if thumbnail else None,
        owner=user,
    )

    return HttpResponse(b"CREATED", status=201)


def is_dummy_user(username):
    import json, os
    from django.conf import settings

    try:
        users_path = os.path.join(settings.BASE_DIR, 'data', 'users.json')
        with open(users_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
            dummy_usernames = [u['username'] for u in users]
            return username in dummy_usernames
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def show_main(request):
    filter_type = request.GET.get("filter", "all")

    if filter_type == "all":
        post_list = Post.objects.all().order_by('-created_at')
    else:
        post_list = Post.objects.filter(owner=request.user).order_by('-created_at')

    posts_with_flag = []
    for post in post_list:
        posts_with_flag.append({
            'instance': post,
            'is_real_user': True,
        })

    context = {
        'name': request.user.username if request.user.is_authenticated else 'Guest',
        'post_list': posts_with_flag,
    }

    return render(request, "forumMain.html", context)

def show_post(request, post_id):
    post = None
    is_owner = False  
    is_real_user = False

    try:
        uuid.UUID(post_id)
        post = get_object_or_404(Post, pk=post_id)
        is_real_user = True

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
                        owner_username = item.get("owner_username", None)
                        is_real_user = owner_username is not None and not is_dummy_user(owner_username)
                        break
        except FileNotFoundError:
            pass

    if not post:
        raise Http404("Post not found")

    context = {
        'post': post if isinstance(post, Post) else None,
        'json_post': post if isinstance(post, dict) else None,
        'is_owner': is_owner, 
        'is_real_user': is_real_user, 
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
@csrf_exempt
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
@csrf_exempt
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id, owner=request.user)

    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"message": "Post updated successfully"})
        
        return redirect("forumModule:show_main")
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"error": form.errors}, status=400)

    return JsonResponse({"error": "Invalid form"}, status=400)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id, owner=request.user)
    post.delete()
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"message": "Post deleted successfully"})
    
    return HttpResponseRedirect(reverse("forumModule:show_main"))

@login_required
@csrf_exempt
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count(),
    })

@login_required
def check_user_liked(request, post_id):
    try:
        post = get_object_or_404(Post, pk=post_id)
        liked = request.user in post.likes.all()
        return JsonResponse({
            'liked': liked,
            'like_count': post.like_count
        })
    except:
        return JsonResponse({'liked': False, 'like_count': 0})

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def add_comment(request, post_id):
    try:
        uuid.UUID(post_id)
    except ValueError:
        return JsonResponse({
            "status": "error",
            "message": "This is a dummy post. Comments are disabled."
        }, status=400)
    
    post = get_object_or_404(Post, pk=post_id)
    content = request.POST.get("content", "").strip()

    if not content:
        return JsonResponse({"error": "Comment cannot be empty."}, status=400)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
    )


    return JsonResponse({
        "status": "success", 
        "message": "Comment added successfully.",
        "comment": {
            "user": comment.author.username,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(), 
        },
        "comment_count": post.comments.count(),
    })

def get_comments(request, post_id):
    is_uuid = True
    try:
        uuid.UUID(post_id)
    except ValueError:
        is_uuid = False

    if is_uuid:
        try:
            post = Post.objects.get(pk=post_id)
            comments = post.comments.select_related("author").order_by("-created_at")
            data = [
                {
                    "user": comment.author.username,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                }
                for comment in comments
            ]
            return JsonResponse(data, safe=False)
        except Post.DoesNotExist:
            raise Http404("Post not found")

    # kalau bukan UUID, ambil dari JSON dummy
    file_path = os.path.join(settings.BASE_DIR, "data", "forum.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            posts = json.load(f)
            for item in posts:
                if str(item.get("id")) == str(post_id):
                    return JsonResponse(item.get("comments", []), safe=False)
    except FileNotFoundError:
        pass

    raise Http404("Post not found")

@csrf_exempt
def show_json(request):
    filter_type = request.GET.get("filter", "all")  
    
    # Filter posts berdasarkan parameter
    if filter_type == "my":
        # Cek apakah user sudah login
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required',
                'message': 'Please login to see your posts'
            }, status=401)
        
        # Filter hanya post milik user yang login
        posts = Post.objects.filter(owner=request.user).select_related('owner').order_by('-created_at')
    else:
        # Tampilkan semua post
        posts = Post.objects.select_related('owner').order_by('-created_at')
    
    # Convert database posts to JSON
    db_data = [
        {
            'id': str(post.id),
            'description': post.description,
            'thumbnail': post.thumbnail,
            'category': post.category,
            'post_views': post.post_views,
            'is_hot': post.is_post_hot,
            'like_count': post.likes.count(), 
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'owner_id': post.owner.id if post.owner else None,
            'owner_username': post.owner.username if post.owner else None,
            'is_owner': (
                request.user.is_authenticated and post.owner == request.user
            ),
            'is_real_user': True,

            'comments': [
                {
                    'user': comment.author.username,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat(),
                }
                for comment in post.comments.all()
            ]
        }
        for post in posts
    ]

    file_data = []
    if filter_type == "all": 
        file_path = os.path.join(settings.BASE_DIR, 'data', 'forum.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                for item in file_data:
                    owner_username = item.get("owner_username")
                    item["is_real_user"] = owner_username is not None and not is_dummy_user(owner_username)
                    if 'comments' not in item:
                        item['comments'] = []
        except FileNotFoundError:
            file_data = []
        except json.JSONDecodeError:
            file_data = []

    combined_data = db_data + file_data

    return JsonResponse(combined_data, safe=False)


def show_json_by_id(request, post_id):
    post = None

    try:
        try:
            uuid.UUID(post_id)
            post = Post.objects.select_related('owner').get(pk=post_id)
        except ValueError:
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
                "like_count": post.likes.count(),
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "owner_id": post.owner.id if post.owner else None,
                "owner_username": post.owner.username if post.owner else None,
                "is_real_user": True, 
                "comments": [
                    {
                        'user': comment.author.username,
                        'content': comment.content,
                        'created_at': comment.created_at.isoformat(),
                    }
                    for comment in post.comments.all()
                ]
            }
            return JsonResponse(data)
    except Exception:
        pass

    file_path = os.path.join(settings.BASE_DIR, 'data', 'forum.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if str(item.get('id')) == str(post_id):
                    owner_username = item.get("owner_username")
                    item["is_real_user"] = owner_username is not None and not is_dummy_user(owner_username)
                    if 'comments' not in item:
                        item['comments'] = []
                    return JsonResponse(item)
    except FileNotFoundError:
        pass

    raise Http404("Post not found")
