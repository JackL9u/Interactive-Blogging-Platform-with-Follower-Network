"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from socialnetwork import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_action, name='home'),
    path('base', views.start_action, name='base'),
    
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    
    path('add-post', views.add_post_action, name='add-post'),
    # path('add-comment', views.add_comment_action, name='add-comment'),
    path('view-profile/<int:userID>', views.view_profile_action, name='view-profile'),
    path('photo/<int:userID>', views.get_photo, name='photo'),
    path('edit-info', views.edit_info_action, name = 'edit-info'),
    path('follow/<int:userID>', views.follow_action, name = 'follow'),
    path('unfollow/<int:userID>', views.unfollow_action, name = 'unfollow'),
    path('follower-stream', views.follower_stream_action, name='follower-stream'),

    path('socialnetwork/get-global', views.get_global_action, name='socialnetwork/get-global'),
    path('socialnetwork/add-comment', views.ajax_add_comment_action, name='socialnetwork/add-comment'),
    path('socialnetwork/get-follower', views.get_follower_action, name='socialnetwork/get-follower'),
]
