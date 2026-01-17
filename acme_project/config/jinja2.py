from jinja2 import Environment  
from django.urls import reverse  
from django.templatetags.static import static
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import date, time, floatformat
import jinja2

def environment(**options):  
    env = jinja2.Environment(**options)
    
    env.filters.update({
        'intcomma': intcomma,
        'date': date,
        'time': time,
        'floatformat': floatformat,
    })
    
    env.globals.update({  
        "static": static,  
        "url": reverse,
        'min': min,
        'max': max,
        'range': range, 
        'now': date,
    })  
    
    return env
