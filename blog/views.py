from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.urls import reverse
import logging
from .models import Post
from django.http import Http404

# Create your views here.

#Static Demo data
# posts = [
#         {'id':1,'title': 'Post 1','content':'Content of Post 1'},
#         {'id':2,'title': 'Post 2','content':'Content of Post 2'},
#         {'id':3,'title': 'Post 3','content':'Content of Post 3'},
#         {'id':4,'title': 'Post 4','content':'Content of Post 4'},
# ]

def index(request):
    blog_title = 'Latest posts'
    # getting data from post model.
    posts = Post.objects.all()
    
    return render(request, 'blogs/index.html',{'blog_title':blog_title, 'posts':posts}) #templates address, variable interpolation

def detail(request, slug):

    # getting static data
    # post = next((item for item in posts if item['id'] == post_id), None)

    try:
        # getting data from model by post id
        post = Post.objects.get(slug=slug)
        related_posts = Post.objects.filter(category = post.category).exclude(pk=post.id)
        
    except Post.DoesNotExist:
        raise Http404("Post Does not Exisit!! ")
    # logger = logging.getLogger("Testing")
    # logger.debug(f'post variable is {post}')

    return render(request, 'blogs/detail.html',{'post':post, 'related_posts':related_posts})

def old_url_redirect(request):
    return redirect(reverse('blog:new_page_url')) #app-name=blog:url_name

def new_url_view(request):
    return HttpResponse("This is the new URL")