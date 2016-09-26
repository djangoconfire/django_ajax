from django.shortcuts import render, redirect, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate , login ,logout
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.db.models import Q
from taggit.models import Tag
from .models import UserPost,Vote,UserProfile,UserComment,UserReply,CommentVote,UserView,PostFlag,Flag 
from . import suggest_settings as SETTINGS 
from forms import CommentForm, PostForm, ReplyForm, UserProfileForm, PostFlagForm
import json
import traceback


#Utility functions 

#To remove newline and carraige returns from dynamically generated
#form tables or other html.
def removenewline(value):
    values = str(value).split('\n')
    values = [value.replace('\r','') for value in values]
    new_value = ''.join(values)
    return unicode(str(new_value))


#To find how ago was a post,comment or reply created or edited
def findtimediff(seconds):
    if(seconds/86400 > 1 ):
        return str(seconds/86400)+" days"
    elif(seconds/86400 == 1):
        return str(seconds/86400)+" day"
    elif(seconds / 3600 > 1):
        return str(seconds/3600)+" hours"
    elif(seconds / 3600 == 1):
        return str(seconds/3600)+" hour"
    elif(seconds / 60 > 1):
        return str(seconds/60)+" minutes"
    elif(seconds / 60 == 1):    
        return str(seconds/60)+" minute"
    else:
        return str(seconds)+" seconds"



#Views for displaying separate html templates


def home(request):
    all_published_posts = UserPost.objects.filter(is_published=True)
    published_post_count = len(all_published_posts)
    popular_posts_list = []

    if(published_post_count > 10):
        popular_posts_list = all_published_posts.order_by('-vote_count','-num_of_views')[:10]
    else:
        popular_posts_list = all_published_posts.order_by('-vote_count','-num_of_views')[:published_post_count]
    vote_list = []
    value = 0
    user = None 
    #If user is logged in 
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        for post in popular_posts_list:
            try:
                vote = Vote.objects.get(post=post,user=user)
                if vote.up_vote == True:
                    value = 1
                elif vote.up_vote == False:
                    value = -1
            except Vote.DoesNotExist as e:
                value = 0
            vote_list.append(value)
        
    if user is None:
        vote_list = [0]*len(popular_posts_list)

    context = { 'popular_posts_list': popular_posts_list, 'user':user,'vote_list':vote_list}
    #The render function calls render_to_string and feeds the result
    #to HttpResponse object suitable for returning from a view
    return render(request, 'suggest/home.html', context) 


def latest(request):
    all_published_posts = UserPost.objects.filter(is_published=True)
    published_post_count = len(all_published_posts)
    latest_posts_list = []

    if(published_post_count > 10):
        latest_posts_list = all_published_posts.order_by('-pub_date')[:10]
    else:
        latest_posts_list = all_published_posts.order_by('-pub_date')[:published_post_count]
    
    vote_list = []
    value = 0   #Representing user's vote on a particular post,1=upvote,0=novote,-1=downvote
    user = None

    #If user is logged in 
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        for post in latest_posts_list:
            try:
                vote = Vote.objects.get(post=post,user=user)
                if vote.up_vote == True:
                    value = 1
                elif vote.up_vote == False:
                    value = -1
            except Vote.DoesNotExist as e:
                value = 0
            vote_list.append(value)
    
    if user is None:
        vote_list = [0]*len(latest_posts_list)

    context = { 'latest_posts_list': latest_posts_list, 'vote_list':vote_list,'user':user}

    return render(request, 'suggest/latest.html', context) 


def tag_home(request):
    user = None 
    #If user is logged in 
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    
    #TODO
    #Improve the fol
    try:
        list_of_tags = Tag.objects.all()
    except Exception as e:
        return render(request,"500.html", {"error" : e})

    tag_post_list = []
    context = {}
    for tag in list_of_tags:
        #Take out all the tagged items under given tag
        post_count = tag.taggit_taggeditem_items.count()
        if post_count != 0:
            tag_post_list.append((tag.slug,tag.name,post_count))
    tag_post_list.sort(key=lambda x: x[2],reverse=True)
    context['tag_post_list']=tag_post_list
    context['user'] = user
    return render(request,'suggest/tag_home.html',context)


def tag(request, tag_slug):
    try:
        posts_under_tag = UserPost.objects.filter(is_published=True,tags__slug=tag_slug).order_by('-vote_count','-num_of_views')
    except Exception as e:
        message = "Requested tag does not exist "
        return render(request,"500.html", {"error" : e,'message':message})

    # posts_under_tag_tuple = ((post,post.vote_set.filter(up_vote=True).count(),post.vote_set.filter(up_vote=False).count()) for post in posts_under_tag)
    vote_list = []
    value = 0
    user = None 

    #If user is logged in 
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        for post in posts_under_tag:
            try:
                vote = Vote.objects.get(post=post,user=user)
                if vote.up_vote == True:
                    value = 1
                elif vote.up_vote == False:
                    value = -1
            except Vote.DoesNotExist as e:
                value = 0
            vote_list.append(value)
    
    if user is None:
        vote_list = [0]*len(posts_under_tag)
    context = {'posts_under_tag':posts_under_tag,'tag_name':tag_slug,'vote_list':vote_list,'user':user}

    return render(request,'suggest/tag.html',context)


def category_home(request):
    user = None 
    #If user is logged in 
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    
    try:
        list_of_categories = UserPost.CHOICES
    except Exception as e:
        return render(request,"500.html", {"error" : e})
                    
    category_post_list = []
    context = {}
    for category in list_of_categories:
        list_of_assoc_posts = UserPost.objects.filter(post_type=category[0],is_published=True).order_by('-vote_count','-num_of_views')
        length = len(list_of_assoc_posts)
        list_of_assoc_posts = list_of_assoc_posts[:5]
        category_post_list.append((category,list_of_assoc_posts,length))
        category_post_list.sort(key=lambda x :x[2],reverse=True)

    context['user'] = user 
    context['category_post_list']=category_post_list
    return render(request,'suggest/category_home.html',context)


def category(request,category_name):
    posts_under_category = UserPost.objects.filter(post_type=category_name).order_by('-vote_count','-num_of_views')
    # posts_under_category = [(post,post.vote_set.filter(up_vote=True).count(),post.vote_set.filter(up_vote=False).count()) for post in posts_under_category]
    context = {}
    context['categoryName'] = dict(UserPost.CHOICES).get(category_name)
    context['posts_under_category'] = posts_under_category
    vote_list = []
    value = 0
    user = None 
    #If user is logged in 
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        for post in posts_under_category:
            try:
                vote = Vote.objects.get(post=post,user=user)
                if vote.up_vote == True:
                    value = 1
                elif vote.up_vote == False:
                    value = -1
            except Vote.DoesNotExist as e:
                value = 0
            vote_list.append(value)
   
    if user is None:
        vote_list = [0]*len(posts_under_category)
    context['vote_list'] = vote_list
    context['user'] = user 
    return render(request,'suggest/category.html',context)


@login_required
def myposts(request,user_name):
    try:
        user = UserProfile.objects.get(username=user_name)
        myposts_list = UserPost.objects.filter(user=user,is_published=True).order_by('-vote_count','-pub_date')
    except Exception as e:
        return render(request,"500.html", {"exception":str(e)})
    
    #To store the vote action of user on each post    
    vote_list = []
    value = 0
    user = None 

    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        
        for post in myposts_list:
            
            try:
                vote = Vote.objects.get(post=post,user=user)
                if vote.up_vote == True:
                    value = 1
                elif vote.up_vote == False:
                    value = -1
            except Vote.DoesNotExist as e:
                value = 0
           
            vote_list.append(value)
  
    if user is None:
        vote_list = [0]*len(myposts_list)

    context = { 'myposts_list': myposts_list, 'user':user,'vote_list':vote_list}

    return render(request, 'suggest/myposts.html', context) 


def userposts(request,user_name):
    try:
        userwhoposted = UserProfile.objects.get(username=user_name)
        userposts_list = UserPost.objects.filter(user=userwhoposted,is_published=True,posted_anonymously=False).order_by('-vote_count','-pub_date')
    except Exception as e:
        return render(request,"500.html", {"error" : e},
                )
    vote_list = []
    value = 0
    user = None 
    #If user is logged in 
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        for post in userposts_list:
            try:
                vote = Vote.objects.get(post=post,user=user)
                if vote.up_vote == True:
                    value = 1
                elif vote.up_vote == False:
                    value = -1
            except Vote.DoesNotExist as e:
                value = 0
            vote_list.append(value)

    if user is None:
        vote_list = [0]*len(userposts_list)

    context = { 'userposts_list': userposts_list, 'user':user,'vote_list':vote_list,'userwhoposted':userwhoposted }

    return render(request, 'suggest/userposts.html', context)


def post(request, post_slug):

    user = None
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user

        try:
            user = UserProfile.objects.get(username=user.username)
        except Exception as e:
            message = "Requested user does not exist "
            return render(request,"500.html", {"error" : e,'message':message},)
    
    try:
        post = UserPost.objects.get(slug=post_slug,is_published=True)

        #If user is logged in then get the user vote action on the given post
        if user != None:
            thisUserUpVote = Vote.objects.filter(post=post,user=user,up_vote=True).count()
            thisUserDownVote = Vote.objects.filter(post=post,user=user,up_vote=False).count()
        
        comment_list = UserComment.objects.filter(post=post,is_published=True).order_by('-vote_count')
        vote_state_list = []    #Representing the state of user vote on each comment

        for comment in comment_list:
            try:
                voteobject = CommentVote.objects.get(comment=comment,user=user)

                if voteobject.up_vote == True:
                    vote_state_list.append(1)
                elif voteobject.up_vote == None:
                    vote_state_list.append(0)
                else:
                    vote_state_list.append(-1)
            #If the vote object is not found then the user has not voted on the comment
            except Exception as e:
                vote_state_list.append(0)

        #Count the number of replies corresponding to each comment
        reply_count_list = []
        reply_count_list = [comment.userreply_set.filter(is_published=True).count() for comment in comment_list]
        
        #Index is comment slug, value is slugs of all the replies to the comment
        reply_slugs_dict = {}
        for comment in comment_list:
            reply_slug_list = [reply.slug for reply in comment.userreply_set.filter(is_published=True)]
            reply_slugs_dict[comment.slug] = reply_slug_list
        reply_slugs_json = json.dumps(reply_slugs_dict)

    except Exception as e:
        message = "Error in post view"
        return render(request,"500.html", {"error":e,'message':message})


    #Increment the number of views for logged in users
    if request.user.is_authenticated():

        #Get the view object from the database
        user_view_on_post = UserView.objects.filter(user=user,post=post)

        #If the object already exists then increment the count
        if user_view_on_post.exists():
            user_view_on_post = user_view_on_post[0]

            #Increment the view count only if the time of the recent view was more than 15 minutes ago.
            if (timezone.now() - user_view_on_post.time_of_recent_view).seconds > 900:
                user_view_on_post.view_count = user_view_on_post.view_count + 1
                post.num_of_views = post.num_of_views + 1

        #Else create a new UserView object
        else:
            user_view_on_post = UserView()
            user_view_on_post.user = user
            user_view_on_post.post = post
            user_view_on_post.view_count = 1
            user_view_on_post.creation_time = timezone.now()
            post.num_of_views = post.num_of_views + 1

        try:
            user_view_on_post.time_of_recent_view = timezone.now()
            user_view_on_post.save()
            post.save()
        except Exception as e:
            return render(request,'500.html',{'exception':str(e),'message':'Error while saving userview or post.'})

    #Store the slugs of all the comments on the given post
    comment_slug_list = []
    for comment in comment_list:
        comment_slug_list.append(comment.slug)

    comment_slug_list = json.dumps(comment_slug_list)
    context ={'post':post,'comment_list':comment_list,'reply_count_list':reply_count_list,'comment_slug_list':comment_slug_list}
    context['reply_slugs_json'] = reply_slugs_json

    urlMap = {}

    if post.is_flagged:
        post_flags_list = []
        flag_objects = PostFlag.objects.filter(post=post).exclude(flag_type='RM')
        for flag in flag_objects:
            post_flags_list.append((flag.flag_type,flag.user_who_flagged.username))
            urlMap[flag.user_who_flagged.username] = str(reverse('suggest:userposts',args=[flag.user_who_flagged.username]))
        context['post_flags_list'] = post_flags_list 
    if user != None:
        urlMap['userposts_url'] = str(reverse('suggest:userposts',args=[user.username]))
        urlMap[user.username] = urlMap['userposts_url']
    context['urlMap'] = json.dumps(urlMap)

    if user != None:
        context['user'] = user
    else:
        thisUserUpVote = 0
        thisUserDownVote = 0
        context['user'] = None
    
    context.update({'thisUserUpVote':thisUserUpVote,'thisUserDownVote':thisUserDownVote})
    context['vote_state_list'] = vote_state_list

    #Create comment and reply forms to be displayed through ajax
    comment_form = CommentForm()
    reply_form = ReplyForm()
    post_flag_form = PostFlagForm()

    context['reply_form'] = reply_form
    context['comment_form'] = comment_form
    context['post_flag_form'] = post_flag_form

    return render(request,'suggest/post.html',context)



#Accounts views



#To handle a new login(successful as well as error) and to present a blank login page to user
def login_view(request):
    context = {}
    context.update(csrf(request))
    if request.method == 'POST':
        username_or_email = request.POST.get('username','')
        email = ''
        if '@' in username_or_email:
            email = username_or_email 
        else:
            username = username_or_email
        password = request.POST.get('password','')

        if email == '':
            user = authenticate(username=username, password=password)
        else:
            if(User.objects.filter(email=email).exists()):
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
            else:
                user = None 

        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('suggest:myposts', args=[user.username]))
        else:
            if email == '':
                error_message = "UserName or Password Invalid"
            else:
                error_message = "Email or Password Invalid"
            context['error_message']=error_message
            return render(request,'login.html',context)
    return render(request,'login.html',context)


#TODO
#This method body is not complete
def logout_view(request):
    logout(request)
    context = {}
    return HttpResponseRedirect('/suggest/accounts/login/') 


#View to render a new signup page as well as a submitted sign up page
def signup_view(request):
    try:
        if request.method == 'POST':
            form = UserProfileForm(data=request.POST)

            if form.is_valid():
                userprofile = form.save(commit=False)
                userprofile.set_password(form.cleaned_data['password'])
                userprofile.save()
                #Redirect to home page
                return HttpResponseRedirect('/suggest/accounts/login')
            else:
                errors =  form.errors 
                args = {}
                args.update(csrf(request))  #Prevent cross site request forgery
                args['form'] = UserProfileForm() #Blank User Creation Form
                args['errors'] = errors 
                #Return a blank form to user for signing again (with or without error)
                return render(request,'signup.html',args)
           
    except Exception as e:
        # print traceback.print_exc()
        return render(request,"500.html", {"error" : e})

    #Add error handling functionality and notification to user
    args = {}
    args.update(csrf(request))  #Prevent cross site request forgery
    args['form'] = UserProfileForm() #Blank User Creation Form

    #Return a blank form to user for signing again (with or without error)
    return render(request,'signup.html',args)



#Views for adding, updating or deleting content


#Non ajax

@login_required
def add_suggestion(request):
    user= request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    try:
        tags = Tag.objects.distinct()
    except Exception as e:
        return render(request,"500.html", {"error" : e})
    postform = PostForm()
    context = {'tags':tags,'user':user,'postform':postform}
    return render(request,'suggest/suggestionform.html',context)

@login_required
def updatepostform(request,post_slug):
    djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    
    try:
        user = UserProfile.objects.get(username=djangouser.username)
        post = UserPost.objects.get(is_published=True,slug=post_slug)
        choices = UserPost.CHOICES
        tags = Tag.objects.distinct()
    except Exception as e:
        return render(request,"500.html", {"error" : e})
    if post.is_closed:
        return render(request,"500.html",{"exception":"The post has been closed.No editing allowed."})
    if post.user.username != user.username:
        return render(request,"500.html", {"error" : "This post doesn't belong to you.You cannot edit it."})
    
    postform = PostForm(instance=post);
    context = {'choices':choices,'tags':tags,'post':post,'postform':postform}
    
    return render(request,'suggest/suggestionform.html',context)


#VIEWS FOR HANDLING AJAX REQUESTS


#TODO
'''
Improve the method for missing values handling
and for form validation and other error handling
'''
@csrf_exempt
@login_required
def createpost(request):
    djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    try:
        choices = UserPost.CHOICES
        tags = Tag.objects.distinct()
        post = UserPost()
        user = UserProfile.objects.get(username=djangouser.username)
        post.user = user
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success':'False','exception':str(e)})

    if request.method == "POST":
        form_data = request.POST.get('formData','')
        form_data_list = json.loads(form_data)

        length = len(form_data_list)
        
        for i in range(length):
            current_dictionary = form_data_list[i]

            if current_dictionary['name'] == 'post_title':
                post.post_title = current_dictionary['value']
                continue

            if current_dictionary['name'] == 'text':
                post.text = current_dictionary['value']
                continue

            if current_dictionary['name'] == 'posted_anonymously':
                post.posted_anonymously = True
                continue

            if current_dictionary['name'] == 'post_type':
                post.post_type = current_dictionary['value']
                try:
                    post.save()
                except Exception as e:
                    return JsonResponse({'success':'False','exception':str(e)})
                continue

            if current_dictionary['name'] == 'as_values_id_tags__tagautosuggest':
                list_of_tags = current_dictionary['value'].split(',')
                for tag in list_of_tags:
                    if tag != '' and tag != None:
                        tagobject = Tag.objects.get(name=tag)
                        post.tags.add(tagobject)
                continue

        try:
            post.save()
        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})

    
    return JsonResponse({'success':'True','post_slug':post.slug})


@csrf_exempt
@login_required
def deletepost(request):
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        userprof = UserProfile.objects.get(username = user.username) 
    
    if request.method == "POST":
        post_slug = request.POST.get('post_slug','')
    else:
        return JsonResponse({'success':'False','exception':'The request method is not POST.'})
    
    try:
        post = UserPost.objects.get(slug=post_slug)
        post.is_published = False
        post.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    return JsonResponse({'success':'True','post_title':post.post_title})


@csrf_exempt
@login_required
def updatepost(request):
    djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    
    try:
        choices = UserPost.CHOICES
        tags = Tag.objects.distinct()
        user = UserProfile.objects.get(username=djangouser.username)
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})
    
    if request.method == "POST":
        form_data = request.POST.get('formData','')
        form_data_list = json.loads(form_data)
        slug = request.POST.get('post_slug','')

        try:
            post = UserPost.objects.get(slug=slug,is_published=True)
        except exception as e:
            return JsonResponse({'success':'False','exception':str(e)})

        if post.is_closed:
            message = "The post has been closed. Updating not allowed."
            return JsonResponse({'success':'False','message':message})

        if post.user.username != user.username:
            return JsonResponse({'success':'False','exception':'The post does not belong to you.'})

        length = len(form_data_list)

        #Set posted_anonymously to False because that won't be passed 
        #in formData if not explicitly selected.
        post.posted_anonymously = False 
        
        for i in range(length):
            current_dictionary = form_data_list[i]

            if current_dictionary['name'] == 'post_title':
                post.post_title = current_dictionary['value']
                continue

            if current_dictionary['name'] == 'text':
                post.text = current_dictionary['value']
                continue

            if current_dictionary['name'] == 'posted_anonymously':
                if current_dictionary['value'] == 'on':
                    post.posted_anonymously = True
                    continue
                else:
                    post.posted_anonymously = False 
                    continue

            if current_dictionary['name'] == 'post_type':
                post.post_type = current_dictionary['value']
                try:
                    post.save()
                except Exception as e:
                    return JsonResponse({'success':'False','exception':str(e)})
                continue

            if current_dictionary['name'] == 'as_values_id_tags__tagautosuggest':
                list_of_tags = current_dictionary['value'].split(',')

                #Clear the previous tags of post
                post.tags.clear()

                #Add the new tags
                for tag in list_of_tags:
                    if tag != '' and tag != None:
                        tagobject = Tag.objects.get(name=tag)
                        post.tags.add(tagobject)
                continue

        try:
            post.last_updated_date = timezone.now()
            post.save()
        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})

    else:
        return JsonResponse({'success':'False','exception':'The request method is not POST.'})
    
    return JsonResponse({'success':'True','post_slug':post.slug})


@csrf_exempt
@login_required
def flagpost(request):

    if request.method == "POST":
        post_slug = request.POST.get('post_slug','')
        form_data = request.POST.get('formData','')
    else:
        return JsonResponse({'success':'False'})

    form_data_list = json.loads(form_data)

    try:
        post = UserPost.objects.get(slug=post_slug,is_published=True)
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user 
    
    try:
        user = UserProfile.objects.get(username=djangouser.username)
    except Exception as e:
        return JsonResponse({'success':'False'})

    #TODO : modify the function to limit the number of flags and the frequency of flagging
    
    flag_object_exists = False
    remove_flag = False  

    length = len(form_data_list)
    for i in range(length):
        dictionary = form_data_list[i]
        if dictionary['name'] == 'flag_type':
            if dictionary['value'] == 'RM':
                remove_flag = True
            else:
                type_of_flag = dictionary['value']
            break

    if(PostFlag.objects.filter(user_who_flagged=user,post=post).exists()):
        post_flag = PostFlag.objects.get(user_who_flagged=user,post=post)
        flag_object_exists = True 
    else:
        post_flag = PostFlag()
    
    if flag_object_exists:   
        if remove_flag:
            post_flag.flag_type = 'RM'
        else:
            post_flag.flag_type = type_of_flag
    else:
        #If the post has bot been flagged by the user and 
        #she is trying to remove a non-existent flag
        if remove_flag:
            return JsonResponse({'success':'True','flag_exists':'False','remove_flag':'True'})
        else:
            post_flag.user_who_flagged = user 
            post_flag.post = post
            post_flag.flag_type = type_of_flag
    
    try:
        post_flag.flag_time = timezone.now()
        post_flag.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    #See if the post is flagged or not

    post_flags_list = []
    flag_objects = PostFlag.objects.filter(post=post).exclude(flag_type='RM')
    num_of_flags = flag_objects.count()

    if num_of_flags == 0:
        post.is_flagged = False
    else:
        post.is_flagged = True 

    try:
        post.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    for flag in flag_objects:
        post_flags_list.append((dict(Flag.CHOICES).get(flag.flag_type),flag.user_who_flagged.username))
     

    return JsonResponse({'success':'True','flag':post_flag.flag_type,'post_flags_list':post_flags_list})

@csrf_exempt
@login_required
def createcomment(request):
    if request.method == 'POST':    
        post_slug = request.POST.get('post_slug','')
        form_data = request.POST.get('formData','')
    else:
        return JsonResponse({'success':'False'})

    form_data_list = json.loads(form_data)

    try:
        post = UserPost.objects.get(slug=post_slug,is_published=True)
    except Exception as e:
        return JsonResponse({'success':'False'})

    if post.is_closed:
        message = "The post has been closed. No commenting allowed."
        return JsonResponse({'success':'False','message':message})

    djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user 
    
    try:
        user = UserProfile.objects.get(username=djangouser.username)
    except Exception as e:
        return JsonResponse({'success':'False'})

    #If the user is commenting on his own post, check the max comment limit
    if post.user == user:
        total_num_of_comments = UserComment.objects.filter(post=post,is_published=True).count()
        num_of_user_comments = UserComment.objects.filter(user=user,post=post,is_published=True).count()

        if total_num_of_comments >= 2:
            fraction_of_user_comments = float(num_of_user_comments)/float(total_num_of_comments)
            if fraction_of_user_comments > SETTINGS.MAX_FRACTION_OF_COMMENTS_ON_OWN_POST:
                message = 'Comment cannot be posted.\nMaximum limit on fraction of comments on your own post exceeded.'
                return JsonResponse({'success':'False','message':message})
    
    comment = UserComment()

    #Assign values to the fields
    comment.user = user
    comment.text = form_data_list[1]['value']

    #TODO
    # Temporary workable code, change in the long run
    # for avoiding errors
    if len(form_data_list) > 2:
        if form_data_list[2]['value'] == 'on':
            comment.posted_anonymously = True 
        else:
            comment.posted_anonymously = False
    
    comment.post = post

    try:
        comment.save()
    except Exception as e:
        return JsonResponse({'success':'False'})

    json_dict = {}
    json_dict['comment_slug'] = comment.slug
    json_dict['comment_text'] = comment.text 
    
    if comment.posted_anonymously:
        usernameoranon = "Anonymous |"
    else:
        link_to_user_posts = reverse('suggest:userposts',kwargs={'user_name':str(user.username)},current_app='suggest')
        usernameoranon = comment.user.first_name+" "+comment.user.last_name +\
        "<a href='"+link_to_user_posts+"' class='text-muted'> (~"+comment.user.username+") |</a>" 

    commented_how_ago = " Just now"
    comment_pub_date = comment.pub_date

    json_dict['usernameoranon'] = usernameoranon
    json_dict['commented_how_ago'] = commented_how_ago
    json_dict['comment_pub_date'] = comment_pub_date
    json_dict['success'] = "True"
    
    return JsonResponse(json_dict)


@login_required
def deletecomment(request):
    if request.user.is_authenticated():
        user= request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        userprof = UserProfile.objects.get(username = user.username) 

    if request.method == "POST":
        comment_slug = request.POST.get('comment_slug','')

    try:
        comment = UserComment.objects.get(slug=comment_slug)
        comment.is_published = False
        comment.save()
    except Exception as e:
        return JsonResponse({'success':'False','error':e})

    return JsonResponse({'success':'True'})


@csrf_exempt
@login_required
def updatecommentform(request):
    if request.method == "POST":
        comment_slug = request.POST.get('comment_slug','')
        try:
            comment = UserComment.objects.get(slug=comment_slug,is_published=True)
        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})

        form = CommentForm(instance=comment)
        form_as_table = removenewline(form.as_table())
        return JsonResponse({'success':'True','form':form_as_table})

    else:
        return JsonResponse({'success':'False','exception':"The ajax method is not post"})


@csrf_exempt
@login_required
def updatecomment(request):
    djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    
    try:
        user = UserProfile.objects.get(username=djangouser.username)
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})
    
    if request.method == "POST":
        data_dict = {}

        form_data = request.POST.get('formData','')
        form_data_list = json.loads(form_data)
        slug = request.POST.get('post_slug','')
        comment_slug = request.POST.get('comment_slug','')
        
        try:
            post = UserPost.objects.get(slug=slug,is_published=True,is_closed=False)
            comment = UserComment.objects.get(slug=comment_slug,is_published=True)
        except exception as e:
            return JsonResponse({'success':'False','exception':str(e)})

        if comment.user.username != user.username:
            return JsonResponse({'success':'False','exception':'The comment does not belong to you.'})

        length = len(form_data_list)

        for i in range(length):
            current_dictionary = form_data_list[i]

            if current_dictionary['name'] == 'text':
                comment.text = current_dictionary['value']
                data_dict['comment_text'] = current_dictionary['value']
                continue

            if current_dictionary['name'] == 'posted_anonymously':
                if current_dictionary['value'] == 'on':
                    comment.posted_anonymously = True 
                    data_dict['posted_anonymously'] = 'True' 
                    continue  
            else:
                comment.posted_anonymously = False
                data_dict['posted_anonymously'] = 'False'


        try:
            comment.last_updated_date = timezone.now()
            comment.save()
        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})
    
    else:
        return JsonResponse({'success':'False','exception':'The request method is not POST.'})

    data_dict['success'] = 'True'
    data_dict['comment_user_username'] = user.username 
    data_dict['comment_user_first_name'] = user.first_name 
    data_dict['comment_user_last_name'] = user.last_name
    
    return JsonResponse(data_dict)


@login_required
def createreply(request):
    if request.method == 'POST':    
        comment_slug = request.POST.get('comment_slug','')
        form_data = request.POST.get('formData','')
    else:
        return JsonResponse({"success":'False','exception':'Request method is not post.'})

    form_data_list = json.loads(form_data)

    try:
        comment = UserComment.objects.get(slug=comment_slug,is_published=True)
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})
    
    if comment.post.is_closed :
        message = "The post has been closed.No further commenting allowed."
        return JsonResponse({'success':'False','message':message})

    djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user 
    
    try:
        user = UserProfile.objects.get(username=djangouser.username)
    except Exception as e:
        return JsonResponse({'success':'False'})
    reply = UserReply()

    reply.user = user
    reply.text = form_data_list[1]['value']

    #TODO
    # Temporary workable code, change in the long run
    # for avoiding errors
    if len(form_data_list) > 2:
        if form_data_list[2]['value'] == 'on':
            reply.posted_anonymously = True 
        else:
            reply.posted_anonymously = False
    
    reply.comment = comment

    try:
        reply.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    json_dict = {}
    json_dict['comment_slug'] = comment.slug 
    json_dict['reply_slug'] = reply.slug
    json_dict['reply_text'] = reply.text 
    if reply.posted_anonymously:
        usernameoranon = "Anonymous |"
    else:
        link_to_user_posts = reverse('suggest:userposts',kwargs={'user_name':str(user.username)},current_app='suggest')
        usernameoranon = reply.user.first_name+" "+reply.user.last_name + "<a href='"+link_to_user_posts\
        +"' class='text-muted'> (~"+reply.user.username+") |</a>" 

        # <a href="{% url 'suggest:userposts' comment.user.username %}" class="text-muted">
    # time_diff = timezone.now() - comment.pub_date 
    # commented_how_ago = "Commented "+findtimediff(time_diff.seconds)+" ago"
    replied_how_ago = " Just now"
    reply_pub_date = reply.pub_date

    json_dict['usernameoranon'] = usernameoranon
    json_dict['replied_how_ago'] = replied_how_ago
    json_dict['reply_pub_date'] = reply_pub_date
    json_dict['success'] = "True"
    return JsonResponse(json_dict)


@csrf_exempt
@login_required
def deletereply(request):
    if request.user.is_authenticated():
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        userprof = UserProfile.objects.get(username = user.username) 

    if request.method == "POST":
        comment_slug = request.POST.get('comment_slug','')
        reply_slug = request.POST.get('reply_slug','')
    else:
        return JsonResponse({'success':'False','exception':'The request method is not POST.'})
    
    try:
        comment = UserComment.objects.get(slug=comment_slug)
        reply = UserReply.objects.get(slug=reply_slug)
        reply.is_published = False
        reply.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})
    json_dict = {'success':'True','reply_slug':reply_slug,'comment_slug':comment_slug}
    
    return JsonResponse(json_dict)


@csrf_exempt
@login_required
def updatereplyform(request):

    if request.is_ajax():
        print "The request for reply updation is ajax request"
    else:
        print "The request for reply updation is not an ajax request"

    if request.method == "POST":
        comment_slug = request.POST.get('comment_slug','')
        reply_slug = request.POST.get('reply_slug','')
        try:
            comment = UserComment.objects.get(slug=comment_slug,is_published=True)
            reply = UserReply.objects.get(slug=reply_slug,is_published=True)
        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})

        if comment.post.is_closed:
            message = "The post has been closed. Replying to comments not allowed."
            return JsonResponse({'success':'False','message':message})
        
        form = ReplyForm(instance=reply)
        form_as_table = removenewline(form.as_table())
        print str(form_as_table)
        return JsonResponse({'success':'True','form':form_as_table})

    else:
        return JsonResponse({'success':'False','exception':"The ajax method is not post"})


@csrf_exempt
@login_required
def updatereply(request):
    djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    
    try:
        user = UserProfile.objects.get(username=djangouser.username)
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})
    
    if request.method == "POST":
        data_dict = {}

        form_data = request.POST.get('formData','')
        form_data_list = json.loads(form_data)
        slug = request.POST.get('post_slug','')
        comment_slug = request.POST.get('comment_slug','')
        reply_slug = request.POST.get('reply_slug','')

        try:
            post = UserPost.objects.get(slug=slug,is_closed=False,is_published=True)
            comment = UserComment.objects.get(slug=comment_slug,is_published=True)
            reply = UserReply.objects.get(slug=reply_slug,is_published=True)

        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})

        if reply.user.username != user.username:
            return JsonResponse({'success':'False','exception':'The reply does not belong to you.'})

        length = len(form_data_list)

        for i in range(length):
            current_dictionary = form_data_list[i]

            if current_dictionary['name'] == 'text':
                reply.text = current_dictionary['value']
                data_dict['reply_text'] = current_dictionary['value']
                continue

            if current_dictionary['name'] == 'posted_anonymously':
                if current_dictionary['value'] == 'on':
                    reply.posted_anonymously = True 
                    data_dict['posted_anonymously'] = 'True' 
                    continue  
            else:
                reply.posted_anonymously = False
                data_dict['posted_anonymously'] = 'False'


        try:
            reply.last_updated_date = timezone.now()
            reply.save()
        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})
    
    data_dict['success'] = 'True'
    data_dict['reply_user_username'] = user.username 
    data_dict['reply_user_first_name'] = user.first_name 
    data_dict['reply_user_last_name'] = user.last_name
    
    return JsonResponse(data_dict) 


@login_required
def profile_view(request):
    return render(request,'suggest/myprofile.html')


@csrf_exempt
@login_required
def voteup(request):
    post_slug = request.POST.get('post_slug','')

    try:
        post = UserPost.objects.get(slug=post_slug)
    except Exception as e:
        return render(request,"500.html", {"error" : e},
                )

    if post.is_closed:
        return JsonResponse({'closed':'True'})
    post_id = post.id 
    #Get user from database.ensure that this view is called only if a user is logged in
    if request.user.is_authenticated():
        djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        user = UserProfile.objects.get(username = djangouser.username)  
    else:
        context = {}
        return render(request,"suggest/accounts/login",context)

    # Check if the user had voted/unvoted on the post in the past
    try:
        voteobject = Vote.objects.get(user=user,post_id=post_id)
        flag = True
    #if user has not voted already then set the Flag to false
    except Vote.DoesNotExist as e:
        flag = False
    #If any other exception occurs then raise error 500
    except Exception as e:
        return render(request,"500.html", {"error" : e},
            )

    if flag == False:
        #Try to create a new vote object, if error then return error 500
        try:
            voteobject = Vote(user=user,post_id=post_id)
            voteobject.save()
        except Exception as e:
            return render(request,"500.html", {"error" : e},
                )
    else:
        voteobject.last_changed = timezone.now()
    state = voteobject.up_vote

    if state == True:
        #Recall vote
        voteobject.up_vote = None
    elif state == None or state == False:
        #Up vote or toggle
        voteobject.up_vote = True
    else:
        #Invalid state
        e = "Invalid voting state"
        return render(request,"500.html", {"error" : e},
            )
    try:
        voteobject.save()
    except Exception as e:
        return render(request,"500.html", {"error" : e},
            )

    try:
        numUpVotes = Vote.objects.filter(post_id=post_id,up_vote=True).count()
        numDownVotes = Vote.objects.filter(post_id=post_id,up_vote=False).count()
        post.vote_count = numUpVotes - numDownVotes
        post.save()
    except Exception as e:
        return render(request,"500.html", {"error" : e},
                )     
    number = numUpVotes - numDownVotes
    diction = {'number': number,'closed':'False'}
    return JsonResponse(diction)


@csrf_exempt
@login_required
def votedown(request):
    post_slug = request.POST.get('post_slug','')

    try:
        post = UserPost.objects.get(slug=post_slug)
    except Exception as e:
        return render(request,"500.html", {"error" : e},
                )

    if post.is_closed:
        return JsonResponse({'closed':'True'})
    post_id = post.id
    #Get user from database.ensure that this view is called only if a user is logged in
    if request.user.is_authenticated():
        djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        user = UserProfile.objects.get(username = djangouser.username)  
    else:
        context = {}
        return render(request,"suggest/accounts/login",context)

    # Check if the user had voted/unvoted on the post in the past
    try:
        voteobject = Vote.objects.get(user=user,post_id=post_id)
        flag = True
    #if user has not voted already then set the Flag to false
    except Vote.DoesNotExist as e:
        flag = False
    #If any other exception occurs then raise error 500
    except Exception as e:
        return render(request,"500.html", {"error" : e},
            )

    if flag == False:
        #Try to create a new vote object, if error then return error 500
        try:
            voteobject = Vote(user=user,post_id=post_id)
            voteobject.save()
        except Exception as e:
            return render(request,"500.html", {"error" : e},
                )
    else:
        voteobject.last_changed = timezone.now()
    state = voteobject.up_vote

    if state == False:
        #Recall vote
        voteobject.up_vote = None
    elif state == None or state == True:
        #Up vote or toggle
        voteobject.up_vote = False
    else:
        #Invalid state
        e = "Invalid voting state"
        return render(request,"500.html", {"error" : e},
            )
    try:
        voteobject.save()
    except Exception as e:
        return render(request,"500.html", {"error" : e},
            )

    try:
        numUpVotes = Vote.objects.filter(post_id=post_id,up_vote=True).count()
        numDownVotes = Vote.objects.filter(post_id=post_id,up_vote=False).count()
        post.vote_count = numUpVotes - numDownVotes
        post.save()
    except Exception as e:
        return render(request,"500.html", {"error" : e},
                )     
    number = numUpVotes - numDownVotes
    diction = {'number': number}
    return JsonResponse(diction)


@csrf_exempt
@login_required
def upcomment(request):
    if request.method == 'POST':
        print "request is post"
        post_slug = request.POST.get('post_slug','')
        comment_slug = request.POST.get('comment_slug',)
    else:
        return JsonResponse({'success':'False'})
    try:
        post = UserPost.objects.get(slug=post_slug,is_published=True,is_closed=False)
        comment = UserComment.objects.get(post=post,slug=comment_slug)
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    if post.is_closed:
        return JsonResponse({'success':'True','closed':'True'})
    post_id = post.id 
    #Get user from database.ensure that this view is called only if a user is logged in
    if request.user.is_authenticated():
        djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        user = UserProfile.objects.get(username = djangouser.username)  
    else:
        return JsonResponse({'success':'False'})

    # Check if the user had voted/unvoted on the post in the past
    try:
        voteobject = CommentVote.objects.get(user=user,comment=comment)
        flag = True
    #if user has not voted already then set the Flag to false
    except CommentVote.DoesNotExist as e:
        flag = False
    #If any other exception occurs then raise error 500
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    if flag == False:
        #Try to create a new vote object, if error then return error 500
        try:
            voteobject = CommentVote(user=user,comment=comment)
            voteobject.save()
        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})
    else:
        voteobject.last_changed = timezone.now()
    state = voteobject.up_vote

    if state == True:
        #Recall vote
        voteobject.up_vote = None
    elif state == None or state == False:
        #Up vote or toggle
        voteobject.up_vote = True
    else:
        #Invalid state
        e = "Invalid voting state"
        return JsonResponse({'success':'False','exception':str(e)})
    try:
        voteobject.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    try:
        numUpVotes = comment.numUpVotes
        numDownVotes = comment.numDownVotes 
        comment.vote_count = numUpVotes - numDownVotes
        comment.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})
   
    number = numUpVotes - numDownVotes
    diction = {'success':'True','number': number,'closed':'False'}
    return JsonResponse(diction)


@csrf_exempt
@login_required
def downcomment(request):
    if request.method == 'POST':
        post_slug = request.POST.get('post_slug','')
        comment_slug = request.POST.get('comment_slug',)
    else:
        return JsonResponse({'success':'False','exception':'The request method is not POST.'})

    try:
        post = UserPost.objects.get(slug=post_slug)
        comment = UserComment.objects.get(post=post,slug=comment_slug)
    except Exception as e:
        JsonResponse({'success':'False','exception':str(e)})

    if post.is_closed:
        return JsonResponse({'closed':'True'})
    post_id = post.id 

    #Get user from database.ensure that this view is called only if a user is logged in
    if request.user.is_authenticated():
        djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        user = UserProfile.objects.get(username = djangouser.username)  
    else:
        return JsonResponse({'success':'False','exception':'The user is not logged in to vote.'})

    # Check if the user had voted/unvoted on the post in the past
    try:
        voteobject = CommentVote.objects.get(user=user,comment=comment)
        flag = True
    #if user has not voted already then set the Flag to false
    except CommentVote.DoesNotExist as e:
        flag = False
    #If any other exception occurs then raise error 500
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    if flag == False:
        #Try to create a new vote object, if error then return error 500
        try:
            voteobject = CommentVote(user=user,comment=comment)
            voteobject.save()
        except Exception as e:
            return JsonResponse({'success':'False','exception':str(e)})
    else:
        voteobject.last_changed = timezone.now()
    state = voteobject.up_vote

    if state == False:
        #Recall vote
        voteobject.up_vote = None
    elif state == None or state == True:
        #Up vote or toggle
        voteobject.up_vote = False
    else:
        #Invalid state
        e = "Invalid voting state"
        return JsonResponse({'success':'False','exception':str(e)})
    
    try:
        voteobject.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    try:
        numUpVotes = comment.numUpVotes
        numDownVotes = comment.numDownVotes 
        comment.vote_count = numUpVotes - numDownVotes
        comment.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})    
    
    number = numUpVotes - numDownVotes
    diction = {'number': number,'closed':'False'}
    return JsonResponse(diction)


@csrf_exempt
@login_required
def postcloseopen(request):
    if request.method == "POST":
        post_slug = request.POST.get('post_slug','')
    else:
        return JsonResponse({'success':'False','exception':'The request method is not POST.'})
    
    #Get user from database.ensure that this view is called only if a user is logged in
    if request.user.is_authenticated():
        djangouser = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        user = UserProfile.objects.get(username=djangouser.username)
    else:
        return JsonResponse({'success':'False','exception':'User not logged in.'})
    
    try:
        post = UserPost.objects.get(slug=post_slug,is_published=True,user=user)
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    data_dict = {}
    if post.is_closed == True:
        post.is_closed = False
        data_dict['is_closed']='False'
    else:
        post.is_closed = True
        data_dict['is_closed']='True' 
        post.closed_date = timezone.now() 
    
    try:
        post.save()
    except Exception as e:
        return JsonResponse({'success':'False','exception':str(e)})

    data_dict['success']='True'
    return JsonResponse(data_dict)



