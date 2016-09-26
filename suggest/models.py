from __future__ import unicode_literals
from taggit_autosuggest.managers import TaggableManager
from taggit.models import Tag
from django.db import models
from autoslug.fields import AutoSlugField
from django.contrib.auth.models import User
from django.utils import timezone
from colorful.fields import RGBColorField
#from tinymce import models as tinymce_models 
import os
import random
#To get the path of user profile picture


def get_image_path(instance , filename):
    return os.path.join('users',str(instance.id), filename)

# Create your models here.

''' username,email,password,firstname and lastname will
be inherited from the superclass User '''

def getHexColor():
    r = lambda: random.randint(0,255)
    return ('#%02X%02X%02X' % (r(),r(),r()))

# Create your models here.
class UserProfile(User):
    likes = models.IntegerField(default=0)
    #The user profile image will be stored at media/users/id/filename
    profile_image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    imagecolor = RGBColorField(default=getHexColor)


#Parent class of UserPost,UserComment and UserReply
class Content(models.Model):
    user = models.ForeignKey( UserProfile, on_delete = models.CASCADE)  #User who posted the content
    pub_date = models.DateTimeField(auto_now_add = True, editable = False)  #Date and Time of Publication
    is_flagged = models.BooleanField(default = False)   #Flagged by some user for irrelevant content    
    last_updated_date = models.DateTimeField(auto_now_add=True) 
    posted_anonymously = models.BooleanField(default = False, verbose_name='Anonymous')   #whether the user posted anonymously or not
    #text = tinymce_models.HTMLField() #Content body
    text = models.TextField(verbose_name='Description')
    is_published = models.BooleanField(default = True)  #For moderation,post not visible if set to False

    def __unicode__(self):
        return self.text

    class Meta:
        abstract = True

    #For finding how long ago the content was published
    def get_time_diff(self):
        return timezone.now() - self.pub_date

    def get_update_time_diff(self):
        return timezone.now() - self.last_updated_date

class UserPost(Content):

    ''' choices for post type '''
    CHOICES = (
            ('re', 'request'),
            ('su', 'suggestion'),
            ('u', 'url'),
        )
    COLORS = {
        're':'#1f7a1f',
        'su':'#800080',
        'u':'#000099',
        }

    post_title = models.CharField(max_length=250, verbose_name="Title") #Title of the post
    post_type = models.CharField(max_length=100, default='re', choices=CHOICES, verbose_name="Post Category") #Type of post
    tags = TaggableManager()    #Tags associated with the post
    slug = AutoSlugField(populate_from='post_title', always_update=False, unique=True, db_index=True)   #SLug to generate URL
    is_closed = models.BooleanField(default=False)    #if set to True,no more commenting allowed on the post 
    closed_date = models.DateTimeField(null=True) #Date when commenting on the post was closed
    num_of_views = models.IntegerField(blank=True, default=0)
    vote_count = models.IntegerField(blank=True,default=0)

    def __unicode__(self):
        return self.post_title

    def calculateUpVotes(self):
        return Vote.objects.filter(post=self,up_vote=True).count()

    def calculateDownVotes(self):
        return Vote.objects.filter(post=self,up_vote=False).count()

    def getPostCategory(self):
        return dict(self.CHOICES).get(self.post_type)

    numUpVotes = property(calculateUpVotes)
    numDownVotes = property(calculateDownVotes)
    category = property(getPostCategory)


class UserComment(Content):

    post = models.ForeignKey(UserPost, db_index = True, on_delete = models.CASCADE) #UserPost with which the content is associated
    slug = AutoSlugField(populate_from = 'text',unique=True)  
    vote_count = models.IntegerField(blank=True,default=0)

    def calculateUpVotes(self):
        return CommentVote.objects.filter(comment=self,up_vote=True).count()

    def calculateDownVotes(self):
        return CommentVote.objects.filter(comment=self,up_vote=False).count()

    numUpVotes = property(calculateUpVotes)
    numDownVotes = property(calculateDownVotes)

    def __unicode__(self):
        return self.text

class UserReply(Content):
    ''' Create the index on comment,
        it will be queried the most '''
    comment = models.ForeignKey(UserComment,db_index = True, on_delete = models.CASCADE)    #UserComment with which the reply is associated
    slug = AutoSlugField(populate_from = 'text', unique = True, db_index = True)

    def __unicode__(self):
        return self.text

class UserView(models.Model):

    ''' The number of times a particular
     user viewed a particular post '''
    view_count = models.IntegerField(default=0)   

    ''' Create the index on post, 
    it will be queried the most '''

    post = models.ForeignKey(UserPost,db_index = True, on_delete = models.CASCADE)  #UserPost with which the view is associated
    user = models.ForeignKey( UserProfile, on_delete = models.CASCADE)  #User who viewed the post
    creation_time = models.DateTimeField(auto_now_add = True, editable = False) #Time of first view
    time_of_recent_view = models.DateTimeField(auto_now_add = True) #Time of most recent view,used for incrementing count

    class Meta:
        unique_together=(('post','user'),)

    def __unicode__(self):
        return '_'.join((self.user,self.post)) 

class Vote(models.Model):
    user = models.ForeignKey( UserProfile, on_delete = models.CASCADE)  #User who voted 
    post = models.ForeignKey(UserPost,null = True, on_delete = models.CASCADE)      #The post on which vote was made
    up_vote = models.NullBooleanField(null = True)  #NULL signifies no vote,True signifies an upvote
    first_voted = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now_add=True)
    class Meta:
        #A vote should be unique wrt a user and post    
        unique_together = (('user','post'),) 

class CommentVote(models.Model):
    user = models.ForeignKey( UserProfile,on_delete = models.CASCADE)
    comment = models.ForeignKey(UserComment,null = True, on_delete = models.CASCADE)
    up_vote = models.NullBooleanField(null = True)  #NULL signifies no vote,True signifies an upvote
    first_voted = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now_add=True)

    class Meta:
        #A vote should be unique wrt a user and post    
        unique_together = (('user','comment'),) 

class Flag(models.Model):

    #The choices for flag types
    CHOICES = (
        ("RM","REMOVE FLAG"),
        ("IR","IRRELEVANT"),
        ("AB","ABUSIVE"),
        ("RP","REPEATED"),
        ("PR","PROMOTION"),
        ("SP","SPAM"),
        )
    #The user who did this flag
    user_who_flagged = models.ForeignKey( UserProfile, null=True)#, on_delete = models.CASCADE)
    #The time of flag
    #null = True because of non-nullable field
    flag_time = models.DateTimeField(auto_now_add = True,null = True)   
    #The type of flag 
    flag_type = models.CharField(max_length = 100,default = "IR", choices = CHOICES)

    class Meta: 
        abstract = True


#A post can have multiple flags associated with it
class PostFlag(Flag):
    post = models.ForeignKey(UserPost, null = True, on_delete = models.CASCADE)
    postflagcolor = RGBColorField(default=getHexColor)
    #Uncomment the following to enforce one flag by a user per post
    '''
    class Meta:
        #A user can have only one flag on a post
        unique_together = ('Flag.user_who_flagged','post')
        '''
    
#A comment can have multiple flags associated with it
class CommentFlag(Flag):
    comment = models.ForeignKey(UserComment, null = True, on_delete = models.CASCADE)
    commentflagcolor = RGBColorField(default=getHexColor)
    #Uncomment the following to enforce one flag by a user per comment
    '''
    class Meta:
        #A user can have only one flag on a comment
        unique_together = ('Flag.user_who_flagged','comment')
        '''

#A reply can have multiple flags associated with it
class ReplyFlag(Flag):
    reply = models.ForeignKey(UserReply, null = True, on_delete = models.CASCADE)
    replyflagcolor = RGBColorField(default=getHexColor)
    #Uncomment the following to enforce one flag by a user per reply
    '''
    class Meta: 
        #A user can have only one flag on a reply
        unique_together = ('Flag.user_who_flagged','reply')
        '''
