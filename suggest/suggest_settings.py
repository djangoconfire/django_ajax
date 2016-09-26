from django.conf import settings

def get(key,default):
	return getattr(settings,key,default)

MAX_FRACTION_OF_COMMENTS_ON_OWN_POST = get('MAX_FRACTION_OF_COMMENTS_ON_OWN_POST',0.666)
MAX_AUTO_SUGGESTIONS_IN_TAGS = get('MAX_AUTO_SUGGESTIONS_IN_TAGS',20) 