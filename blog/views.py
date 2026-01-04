from django.http import HttpResponse
from django.urls import reverse
import logging
from .models import Category, Post, AboutUs
from django.http import Http404
from django.core.paginator import Paginator
from .forms import ContactForm, ForgotPasswordForm, LoginForm, PostForm, RegisterForm, ResetPasswordForm

#accounts/views.py
from django.shortcuts import render , redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
from django.contrib.auth.models import User

from blog import forms
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail

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
            return redirect("blog:login")


    return render(request, 'blogs/register.html',{'form': form})

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        #login form
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                auth_login(request, user)
                print('LOGIN SUCCESS')
                return redirect("blog:dashboard") # redirect to dashboard
    return render(request, 'blogs/login.html',{'form': form})

def dashboard(request):
    blog_title = 'My Posts'
    #getting user posts
    all_posts =  Post.objects.filter(user=request.user)

    #paginate
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number) 

    return render(request, 'blogs/dashboard.html',{'blog_title':blog_title, 'page_obj':page_object})

def logout(request):
    auth_logout(request)
    return redirect("blog:index")

def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == 'POST':
        #form 
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            #send email to reset password
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)  #http://127.0.0.1:8000
            domain = current_site.domain
            subject = 'Reset Password Requested.'
            message = render_to_string('blogs/reset_password_email.html',{'domain':domain,
            'uidb64':uid, 
            'token':token
            })

            send_mail(subject=subject,
                    message=message,
                    from_email='noreply@gmail.com',
                    recipient_list=[email])
            messages.success(request,'Email has been sent.')

    return render(request, 'blogs/forgot_password.html',{'form':form})

def reset_password(request, uidb64, token):
    form = ResetPasswordForm()
    if request.method == 'POST':
        #form
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            
            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('blog:login')
            else:
                messages.error(request,'The password reset link is invalid.')

    return render(request, 'blogs/reset_password.html',{'form':form})

def new_post(request):
    categories = Category.objects.all()
    form = PostForm()
    if request.method == 'POST':
        #form
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            post.user = request.user
            post.save()
            return redirect('blog:dashboard')
    return render(request, 'blogs/new_post.html',{'categories':categories,'form':form})