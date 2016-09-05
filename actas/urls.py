from django.conf.urls import url

from .views import index, lista, acta_base, subir, subir_validar, subir_confirmar,get_participantes,bajar_propuestas


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^lista$', lista, name='lista'),
    url(r'^base/(?P<id>\d+)$', acta_base, name='base'),
    url(r'^subir/$', subir, name='subir'),
    url(r'^subir/validar$', subir_validar, name='validar'),
    url(r'^subir/confirmar$', subir_confirmar, name='confirmar'),
    url(r'^bajartext$', get_participantes, name='get_participantes'),
    url(r'^bajartodo$', bajar_propuestas, name='bajar_propuestas'),
]
