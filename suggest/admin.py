from django.contrib import admin
from models import Content, UserProfile, UserPost, UserComment, UserReply, UserView, Vote, Flag, ReplyFlag, PostFlag, CommentFlag

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(UserPost)
admin.site.register(UserComment)
admin.site.register(UserReply)
admin.site.register(UserView)
admin.site.register(Vote)
admin.site.register(ReplyFlag)
admin.site.register(PostFlag)
admin.site.register(CommentFlag)
