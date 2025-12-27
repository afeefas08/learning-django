from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.urls import reverse

# Create your views here.

def index(request):
    blog_title = 'Latest posts'
    posts = [
        {'id':1,'title': 'Post 1','content':'Content of Post 1'},
        {'id':2,'title': 'Post 2','content':'Content of Post 2'},
        {'id':3,'title': 'Post 3','content':'Content of Post 3'},
        {'id':4,'title': 'Post 4','content':'Content of Post 4'},
    ]
    return render(request, 'blogs/index.html',{'blog_title':blog_title, 'posts':posts}) #templates address, variable interpolation

def detail(request, post_id):
    return render(request, 'blogs/detail.html')

def old_url_redirect(request):
    return redirect(reverse('blog:new_page_url')) #app-name=blog:url_name

def new_url_view(request):
    return HttpResponse("This is the new URL")