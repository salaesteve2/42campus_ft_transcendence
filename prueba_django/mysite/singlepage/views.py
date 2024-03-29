from django.shortcuts import render
from django.http import HttpResponse, Http404
from general.views import activate_language

def index(request):
    activate_language(request)
    return render(request, "singlepage/index.html")

def home_section(request):
    activate_language(request)
    # Aquí debes escribir el código para obtener y renderizar el contenido de la sección "home"
    # Puedes usar plantillas de Django o devolver HTML directamente
    return render(request, 'base/home_t.html')  # Ajusta el nombre de la plantilla según corresponda

def section(request, num):
    if 1 <= num <= 3:
        return HttpResponse(texts[num-1])
    else:
        raise Http404("No such section")