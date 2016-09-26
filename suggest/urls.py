from django.conf.urls import url,include
from . import views
from django.conf import settings
app_name = 'suggest'
urlpatterns = [
    #By default the home view shows the trending posts 
    url(r'^home/$', views.home, name='home'),
    url(r'^latest/',views.latest,name='latest'),
    url(r'^accounts/login/', views.login_view, name='login'),
    url(r'^accounts/logout$',views.logout_view,name='logout_view'),
    url(r'^accounts/signup$',views.signup_view,name='signup_view'),
    url(r'^accounts/profile/$',views.profile_view,name='profile_view'),
    url(r'^posts/(?P<post_slug>[-\w]+)/$', views.post, name = 'post'),
    url(r'^posts/(?P<post_slug>[-\w]+)/edit$', views.updatepostform, name = 'updatepostform'),
    url(r'^tags$',views.tag_home,name="tag_home"),
    url(r'^tags/(?P<tag_slug>[-\w]+)/$', views.tag, name='tag'),
    url(r'^categories$',views.category_home,name='category_home'),
    url(r'^categories/(?P<category_name>[-\w]+)/$',views.category,name='category'),
    url(r'^addsuggestion$',views.add_suggestion,name='add_suggestion'),
    url(r'^myposts/(?P<user_name>[-\w]+)/$',views.myposts,name='myposts'),
    url(r'^userposts/(?P<user_name>[-\w]+)/$',views.userposts,name='userposts'),

    #Ajax urls

    #Related to post
    url(r'^createpost/$',views.createpost,name='createpost'),
    url(r'^updatepost/$',views.updatepost,name='updatepost'),
    url(r'^deletepost/$',views.deletepost,name='deletepost'),
    url(r'^post/voteup',views.voteup,name='voteup'),
    url(r'^post/votedown',views.votedown,name='votedown'),
    url(r'^post/closeopen',views.postcloseopen,name='postcloseopen'),
    url(r'^post/flagpost/',views.flagpost,name='flagpost'),
    
    #Related to comment
    url(r'^createcomment/$',views.createcomment,name='createcomment'),
    url(r'^updatecommentform/$',views.updatecommentform,name='updatecommentform'),
    url(r'^updatecomment/$',views.updatecomment,name='updatecomment'),
    url(r'^deletecomment/$',views.deletecomment,name='deletecomment'),
    url(r'^post/comment/voteup',views.upcomment,name='upcomment'),
    url(r'^post/comment/votedown',views.downcomment,name='downcomment'),

    #Related to reply
    url(r'^createreply/$',views.createreply,name='createreply'), 
    url(r'^updatereplyform/$',views.updatereplyform,name='updatereplyform'),
    url(r'^updatereply/$',views.updatereply,name='updatereply'),
    url(r'^deletereply/$',views.deletereply,name='deletereply'),

]
      
