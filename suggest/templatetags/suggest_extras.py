from django import template
from suggest.models import UserPost, Flag
register = template.Library()

@register.filter(name="findtimediff")
def findtimediff(seconds):
	if(seconds / 3600 > 1):
		return str(seconds/3600)+" hours"
	elif(seconds / 3600 == 1):
		return str(seconds/3600)+" hour"
	elif(seconds / 60 > 1):
		return str(seconds/60)+" minutes"
	elif(seconds / 60 == 1):	
		return str(seconds/60)+" minute"
	else:
		return str(seconds)+" seconds"

#Filter to access values of keys in a dictionary
@register.filter(name='get_item')
def get_item(dictionary,key):
	return dictionary.get(key)

@register.filter(name='startswith')
def startswith(value,string):
	return value.startswith(string)

@register.filter(name='index')
def index(List, i):
    return List[int(i)]

@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg

@register.filter(name='expand')
def expand(value):
	return dict(UserPost.CHOICES).get(value,'None')

@register.filter(name='removenewline')
def removenewline(value):
	values = str(value).split('\n')
	values = [value.replace('\r','') for value in values]
	new_value = ' '.join(values)
	return str(new_value)

@register.filter(name='getcolor')
def getcolor(value):
	return UserPost.COLORS[value]

@register.filter(name='mod3')
def mod3(value):
	if value%3 == 0:
		return True
	return False
	
@register.filter(name='get_full_flag_name')
def get_full_flag_name(value):
	return dict(Flag.CHOICES).get(value,'')