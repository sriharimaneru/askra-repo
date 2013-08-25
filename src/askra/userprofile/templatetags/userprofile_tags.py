from django import template

register = template.Library()

def key(d, key_name):
    return d[key_name]

def multdec(value, num):
    return value*num/10
    
def facet_url(value):
    if value.rfind("?") == -1 :
        return value + "?"
    else:
        return value + "&"


multdec = register.filter('multdec', multdec)
key = register.filter('key', key)
facet_url = register.filter('facet_url', facet_url)