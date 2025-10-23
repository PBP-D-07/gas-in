from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from apps.forumModule.forms import PostForm
from apps.forumModule.models import Post
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings

def show_main(request):
    filter_type = request.GET.get("filter", "all")

    if filter_type == "all":
        post_list = Post.objects.all()
    else:
        post_list = Post.objects.filter(owner=request.user)

    context = {
        'name': request.user.username if request.user.is_authenticated else 'Guest',
        'post_list': post_list,
    }

    return render(request, "forumMain.html", context)


def show_post(request, id):
    post = get_object_or_404(Post, pk=id)
    context = {'post': post}
    return render(request, 'post_detail.html', context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user  # ganti dari .author ke .owner
            post.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Post created successfully'})
            return redirect("forumModule:show_main")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Invalid form'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id, owner=request.user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('forumModule:show_main')

    context = {'form': form}
    return render(request, "edit_post.html", context)


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id, owner=request.user)
    post.delete()
    return HttpResponseRedirect(reverse('forumModule:show_main'))

def show_json(request):
    post_list = Post.objects.select_related('owner').all()
    data = [
        {
            'id': str(post.id),
            'description': post.description,
            'thumbnail': post.thumbnail.url if post.thumbnail else None,
            'category': post.category,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'owner_username': post.owner.username if post.owner else None,
            'owner_id': post.owner.id if post.owner else None,
        }
        for post in post_list
    ]
    return JsonResponse(data, safe=False)


def show_json_by_id(request, post_id):
    try:
        post = Post.objects.select_related('owner').get(pk=post_id)
        data = {
            'id': str(post.id),
            'description': post.description,
            'thumbnail': post.thumbnail.url if post.thumbnail else None,
            'category': post.category,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'owner_id': post.owner.id if post.owner else None,
            'owner_username': post.owner.username if post.owner else None,
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)
