from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.urls import reverse
import logging
from .models import Post, AboutUs
from django.http import Http404
from django.core.paginator import Paginator
from .forms import ContactForm, RegisterForm
from django.contrib import messages

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
    all_posts = Post.objects.all()
    
    #paginate
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)

    return render(request, 'blogs/index.html',{'blog_title':blog_title, 'page_obj':page_object}) #templates address, variable interpolation

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

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        logger = logging.getLogger("TESTING")
        if form.is_valid():
            logger.debug(f"POST Data is {form.cleaned_data['name']} {form.cleaned_data['email']} {form.cleaned_data['message']}")
            #send email or save in database
            success_message = 'Your Email has been sent!'
            return render(request, 'blogs/contact.html',{'form':form,'success_message':success_message})
            
        else:
            logger.debug("Form validation failure")
            return render(request, 'blogs/contact.html',{'form':form,'name':name,'email':email, 'message':message})
    return render(request, 'blogs/contact.html')

def about(request):
    about_content = AboutUs.objects.first()
    if about_content is None or not about_content.content:
        about_content = "Default content goes here." # Default text
    else:
        about_content = about_content.content
    return render(request, 'blogs/about.html',{'about_content':about_content})

def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # user data created
            user.set_password(form.cleaned_data['password'])  #hashing password.
            user.save()
            messages.success(request, 'Registration Successfull. You can log in.')


    return render(request, 'blogs/register.html',{'form': form})