from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseForbidden

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone

from socialnetwork.forms import EntryForm, LoginForm, RegisterForm, ProfileForm

from socialnetwork.models import Post, Comment, Profile

from datetime import datetime
from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers


import json

def start_action (request):
    return render(request, 'socialnetwork/base.html', {'nameLink': "your name"})

@login_required
def home_action(request):   
    context = {}
    # Just display the registration form if this is a GET request.
    context['page_name'] = 'Global Stream'
    context['username'] = request.user.username
    return render(request, 'socialnetwork/global.html', context)

def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        context['page_name'] = 'Login'
        return render(request, 'socialnetwork/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)

    context['form'] = form
    context['page_name'] = 'Login'
    context['allPosts'] = Post.objects.all()

     # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    context['page_name'] = 'Global Stream'

    login(request, new_user)
    return redirect(reverse('home'))

@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        context['page_name'] = 'Register'
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form
    context['page_name'] = 'Register'

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    user = new_user
    userID = new_user.id
    username = form.cleaned_data['username']
    email = form.cleaned_data['email']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']


    new_profile = Profile(user = user, userID = userID, username = username, email = email, first_name = first_name, last_name = last_name)
    new_profile.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])


    login(request, new_user)
    return redirect(reverse('home'))

@login_required
def add_post_action(request):
    if request.method == 'GET':
        return redirect(reverse('home'))

    if 'newpost' not in request.POST or not request.POST['newpost']:
        return redirect(reverse('home'))
    
    text = request.POST['newpost']
    user = request.user
    user_profile = Profile.objects.get(userID=request.user.id)
    time = timezone.now()

    new_post = Post(text = text, user = user, user_profile = user_profile, time = time)
    new_post.save()

    return redirect(reverse('home'))

@login_required
def view_profile_action(request, userID):
    profile_instance = Profile.objects.get(userID=userID)
    self_profile = Profile.objects.get(userID=request.user.id)
    context = {'profile' : profile_instance, "self_profile" : self_profile}
    if request.user.id == userID:
        context['form'] = ProfileForm(initial={'bio' : profile_instance.bio})
        context['page_name'] = request.user.first_name + ' ' + request.user.last_name + ' ' + "Profile"
        return render(request, 'socialnetwork/selfprofile.html', context)
    else:
        context['page_name'] = profile_instance.user.first_name + ' ' + profile_instance.user.last_name + ' ' + "Profile"
        return render(request, 'socialnetwork/otherprofile.html', context)

@login_required
def get_photo(request, userID):
    profile = get_object_or_404(Profile, userID=userID)
    print('Picture #{} fetched from db: {} (type={})'.format(id, profile.profile_picture, type(profile.profile_picture)))

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not profile.profile_picture:
        raise Http404

    return HttpResponse(profile.profile_picture, content_type=profile.content_type)

@login_required
def edit_info_action(request):
    context = {}

    profile_instance = Profile.objects.get(userID=request.user.id)
    form = ProfileForm(request.POST, request.FILES, instance=profile_instance)
    if not form.is_valid():
        context['form'] = form
    else:
        pic = form.cleaned_data['profile_picture']
        print('Uploaded picture: {} (type={})'.format(pic, type(pic)))

        profile_instance.content_type = form.cleaned_data['profile_picture'].content_type
        form.save()
        context['form'] = ProfileForm(initial={'bio' : profile_instance.bio})
    context['profile'] = profile_instance
    context['page_name'] = request.user.first_name + ' ' + request.user.last_name + ' ' + "Profile"

    return render(request, 'socialnetwork/selfprofile.html', context)

@login_required
def follow_action(request, userID):
    self_profile = Profile.objects.get(userID=request.user.id)
    other_profile = Profile.objects.get(userID=userID)
    self_profile.followed_users.add(other_profile)
    self_profile.save()
    
    context = {'profile' : other_profile, "self_profile" : self_profile}
    context['page_name'] = "Profile Page for " + other_profile.user.first_name + ' ' + other_profile.user.last_name

    return render(request, 'socialnetwork/otherprofile.html', context)

@login_required
def unfollow_action(request, userID):
    self_profile = Profile.objects.get(userID=request.user.id)
    other_profile = Profile.objects.get(userID=userID)
    self_profile.followed_users.remove(other_profile)
    self_profile.save()
    
    context = {'profile' : other_profile, "self_profile" : self_profile}
    context['page_name'] = "Profile Page for " + other_profile.user.first_name + ' ' + other_profile.user.last_name

    return render(request, 'socialnetwork/otherprofile.html', context)

@login_required
def follower_stream_action(request):
    context = {}
    context['page_name'] = 'Follower Global Stream'
    self_profile = Profile.objects.get(userID=request.user.id)
    context["self_profile"] = self_profile
    context['allPosts'] = Post.objects.all()
    return render(request, 'socialnetwork/follower.html', context)


def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)


def get_global_action(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    response_data = []
    
    for post in Post.objects.all():
        comment_list = []
        
        for comment in post.related_comments.all():
            comment_item = {
                'id' : comment.id,
                'comment_user_id' : comment.user.id,
                'comment_user_first_name' : comment.user.first_name,
                'comment_user_last_name' : comment.user.last_name,
                'text' : comment.text,
                'time' : comment.time.isoformat(),
            }
            comment_list.append(comment_item)

        post_info = {
            'id' : post.id,
            'post_user_id' : post.user.id,
            'post_user_first_name' : post.user.first_name,
            'post_user_last_name' : post.user.last_name,
            'text': post.text,
            'time' : post.time.isoformat(),
            'comments' : comment_list,
        }

        response_data.append(post_info)
    
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')


def ajax_add_comment_action(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    if 'comment_text' not in request.POST or not request.POST['comment_text']:
        return _my_json_error_response("You must enter an item to add.", status=400)

    if 'post_id' not in request.POST or not request.POST['post_id']:
        return _my_json_error_response("You must include the post_id or provide a valid post_id.", status=400)

    if not request.POST['post_id'].isdigit():
        return _my_json_error_response("You must provide an int", status=400)

    if int(request.POST['post_id']) > Post.objects.count():
        return _my_json_error_response("it should be less than total num of posts", status=400)

    text = request.POST['comment_text']
    user = request.user
    time = timezone.now()

    new_comment = Comment(text = text, user = user, time = time)
    new_comment.save()

    postNum = request.POST['post_id']
    postInstance = Post.objects.get(id=postNum)
    postInstance.related_comments.add(new_comment)
    postInstance.save()

    response_data = []
    comment_list = []
    
    for comment in postInstance.related_comments.all():
        comment_item = {
            'id' : comment.id,
            'comment_user_id' : comment.user.id,
            'comment_user_first_name' : comment.user.first_name,
            'comment_user_last_name' : comment.user.last_name,
            'text' : comment.text,
            'time' : comment.time.isoformat(),
        }
        comment_list.append(comment_item)
    post_info = {
        'id' : postInstance.id,
        'post_user_id' : postInstance.user.id,
        'post_user_first_name' : postInstance.user.first_name,
        'post_user_last_name' : postInstance.user.last_name,
        'text': postInstance.text,
        'time' : postInstance.time.isoformat(),
        'comments' : comment_list,
    }
    response_data.append(post_info)

    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

@login_required
def get_follower_action(request):
    
    response_data = []
    self_profile = Profile.objects.get(userID=request.user.id)

    for post in Post.objects.all():
        if post.user_profile in self_profile.followed_users.all():

            comment_list = []
            for comment in post.related_comments.all():
                comment_item = {
                    'id' : comment.id,
                    'comment_user_id' : comment.user.id,
                    'comment_user_first_name' : comment.user.first_name,
                    'comment_user_last_name' : comment.user.last_name,
                    'text' : comment.text,
                    'time' : comment.time.isoformat(),
                }
                comment_list.append(comment_item)
            post_info = {
                'id' : post.id,
                'post_user_id' : post.user.id,
                'post_user_first_name' : post.user.first_name,
                'post_user_last_name' : post.user.last_name,
                'text': post.text,
                'time' : post.time.isoformat(),
                'comments' : comment_list,
            }
            response_data.append(post_info)
    
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')