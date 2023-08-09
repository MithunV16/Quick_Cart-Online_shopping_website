from django import template

register=template.Library()

@register.filter(name='get_val')

def get_val(dict,key):
    return dict.get(key)

@register.filter(name='slice_str')
def slice_str(str):
    if(len(str)<12):
        return str
    else:
        return str[:13]+"..."