from django.shortcuts import get_object_or_404, redirect, render
from apps.forumModule.forms import PostForm
from apps.forumModule.models import Post
from django.http import HttpResponse
from django.core import serializers

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


def show_post(request, id):
    post = get_object_or_404(Post, pk=id)
    post.increment_views()

    context = {
        'post': post
    }

    return render(request, "post_detail.html", context)

def show_xml(request):
     post_list = Post.objects.all()
     xml_data = serializers.serialize("xml", post_list)
     return HttpResponse(xml_data, content_type="application/xml")

def show_xml_by_id(request, post_id):
   try:
       post_item = Post.objects.filter(pk=post_id)
       xml_data = serializers.serialize("xml", post_item)
       return HttpResponse(xml_data, content_type="application/xml")
   except Post.DoesNotExist:
       return HttpResponse(status=404)

def show_json(request):
    post_list = Post.objects.all()
    json_data = serializers.serialize("json", post_list)
    return HttpResponse(json_data, content_type="application/json")

def show_json_by_id(request, post_id):
   try:
       post_item = Post.objects.get(pk=post_id)
       json_data = serializers.serialize("json", [post_item])
       return HttpResponse(json_data, content_type="application/json")
   except Post.DoesNotExist:
       return HttpResponse(status=404)