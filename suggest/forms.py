''' Add model based forms in this file
'''
from django import forms
from django.forms import ModelForm
from suggest.models import UserPost, UserComment, UserReply, UserProfile, PostFlag
from django import forms
from taggit.forms import TagWidget
#from tinymce.widgets import TinyMCE

class PostForm(ModelForm):
    # text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = UserPost
        fields = ['post_title','text','posted_anonymously','post_type','tags']

        labels = {
            'post_title':'Title*',
            'text':'Description*',
            'posted_anonymously':'Post Anonymously',
            'post_type':'Category*',
            'tags':'Add Tag(s)',
        }

        widgets = {
        # 'text':forms.Textarea(
        #     attrs={'id':'post-text','required':True, 'placeholder':'Describe your request,suggestion or url','class':'form-control'}
        #     ),
        'post_title':forms.TextInput(
            attrs={'size': 80,'class':'form-control'}
            ),
        'post_type':forms.Select(
            attrs={'class':'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm,self).__init__(*args, **kwargs)

        for fieldname in ['tags']:
            self.fields[fieldname].help_text = None

class CommentForm(ModelForm):
    class Meta:
        model = UserComment
        fields = ['text','posted_anonymously']
        labels = {
            'text': 'Comment Text*',
        }
        widgets = {
            'text': forms.Textarea(
                attrs={'id': 'comment-text', 'required': True, 'placeholder': 'Say something...','class':'form-control comment-form',}
            ),
        }

class ReplyForm(ModelForm):
    class Meta:
        model = UserReply
        fields = ['text','posted_anonymously']
        labels = {
            'text': 'Reply Text*',
        }
        widgets = {
            'text':forms.Textarea(
                attrs={'id': 'reply-text', 'required': True, 'placeholder': 'Reply something...','class':'form-control reply-form'}
                )
        }

class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
        fields = ['first_name','last_name','username','email','password']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'username': 'Username*',
            'email':'Email ID*',
            'password':'Password*',
        }

        widgets = {
            'first_name':forms.TextInput(
                attrs={'id':'first-name', 'placeholder': 'Ritu','class':'form-control'}
                ),
            'last_name':forms.TextInput(
                attrs={'id':'last-name','placeholder':'Raj','class':'form-control'}
                ),
            'username':forms.TextInput(
                attrs={'id':'user-name','placeholder':'ritupycon','class':'form-control'}
                ),
            'email':forms.EmailInput(
                attrs={'id':'email','placeholder':'ritu31195@gmail.com','class':'form-control'}
                ),
            'password':forms.PasswordInput(
                attrs={'id':'password','placeholder':'*************','class':'form-control'}
                ),
        }

        help_texts = {
        'username':"",
        }

class PostFlagForm(ModelForm):

    class Meta:
        model = PostFlag 
        fields = ['flag_type']

        labels = {
            'flag_type': 'Flag',
        }

        widgets = {
            'flag_type': forms.Select(
                attrs={'id':'postflag-type','class':'form-control'}
                ),
        }
