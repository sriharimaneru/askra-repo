from django import template

register = template.Library()

def key(d, key_name):
    return d[key_name]

def multdec(value, num):
	return value*num/10
    
multdec = register.filter('multdec', multdec)
key = register.filter('key', key)