from django.shortcuts import get_object_or_404, redirect, render
from apps.forumModule.forms import PostForm
from apps.forumModule.models import Post
from django.http import HttpResponseRedirect, JsonResponse

# Create your views here.
def show_main(request):
    filter_type = request.GET.get("filter", "all")  # default 'all'

    if filter_type == "all":
        post_list = Post.objects.all()
    else:
        post_list = Post.objects.filter(user=request.user)

    context = {
    'name': request.user.username,
    'post_list': post_list,
    }

    return render(request, "main.html",context)

def create_post(request):
    form = PostForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        post_entry = form.save(commit=False)
        post_entry.user = request.user  # hubungkan dengan user yang login
        post_entry.save()
        return redirect('main:show_main')  # ubah ke view daftar postingan kamu

    context = {
        'form': form
    }

    return render(request, "create_post.html", context)

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
