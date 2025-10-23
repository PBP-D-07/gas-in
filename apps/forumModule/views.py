from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from apps.forumModule.forms import PostForm
from apps.forumModule.models import Post
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

# Create your views here.
def show_main(request):
    filter_type = request.GET.get("filter", "all") 

    if filter_type == "all":
        post_list = Post.objects.all()
    else:
        post_list = Post.objects.filter(user=request.user)

    context = {
    'name': request.user.username,
    'post_list': post_list,
    }

    return render(request, "forumMain.html",context)

def show_post(request, id):
    context = {'post_id': id}
    return render(request, 'post_detail.html', context)

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Post created successfully'})
            return redirect("forumModule:show_main")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Invalid form'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('main:show_main')

    context = {
        'form': form
    }

    return render(request, "edit_post.html", context)

def delete_post(request, id):
    post = get_object_or_404(Post, pk=id)
    post.delete()
    return HttpResponseRedirect(reverse('main:show_main'))

def show_json(request):
    post_list = Post.objects.select_related('author').all()
    data = [
        {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username if post.author else None,
            'user_id': post.author.id if post.author else None,  # 🔥 tambahin ini
            'post_views': post.post_views,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'is_post_hot': post.is_post_hot,
        }
        for post in post_list
    ]
    return JsonResponse(data, safe=False)


def show_json_by_id(request, post_id):
    try:
        post = Post.objects.select_related('author').get(pk=post_id)
        data = {
            'id': str(post.id),
            'title': post.title,
            'content': post.content,
            'post_views': post.post_views,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'updated_at': post.updated_at.isoformat() if post.updated_at else None,
            'is_post_hot': post.is_post_hot,
            'author_id': post.author.id if post.author else None,
            'author_username': post.author.username if post.author else None,
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)
