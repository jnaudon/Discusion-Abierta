# -*- coding: utf-8 -*-
import json

from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from .libs import verificar_rut, verificar_cedula
from .models import Comuna, Acta, Item, GrupoItems, ActaRespuestaItem


PARTICIPANTES_MIN = 4
PARTICIPANTES_MAX = 10


def index(request):
    return render(request, 'index.html')


def lista(request):
    return render(request, 'lista.html')


@ensure_csrf_cookie
def subir(request):
    return render(request, 'subir.html')


def obtener_base(request):
    acta = {
        'min_participantes': PARTICIPANTES_MIN,
        'max_participantes': PARTICIPANTES_MAX,
        'geo': {},
        'participantes': [{} for _ in range(PARTICIPANTES_MIN)]
    }

    acta['itemsGroups'] = [g.to_dict() for g in GrupoItems.objects.all().order_by('orden')]

    return JsonResponse(acta)


def _validar_datos_geograficos(acta):
    errores = []

    comuna_seleccionada = acta.get('geo', {}).get('comuna')
    provincia_seleccionada = acta.get('geo', {}).get('provincia')
    region_seleccionada = acta.get('geo', {}).get('region')

    if type(region_seleccionada) != int:
        return ['Región inválida']

    if type(provincia_seleccionada) != int:
        return ['Provincia inválida']

    if type(comuna_seleccionada) != int:
        return ['Comuna inválida']

    comunas = Comuna.objects.filter(pk=comuna_seleccionada)

    if len(comunas) != 1:
        errores.append('Comuna inválida.')
    else:
        if comunas[0].provincia.pk != provincia_seleccionada:
            errores.append('Provincia no corresponde a la comuna.')

        if comunas[0].provincia.region.pk != region_seleccionada:
            errores.append('Región no corresponde a la provincia.')

    return errores


def _validar_participante(participante, pos):
    errores = []

    if not verificar_rut(participante.get('rut')):
        errores.append('RUT del participante {0:d} es inválido.'.format(pos))

    nombre = participante.get('nombre')
    apellido = participante.get('apellido')

    if type(nombre) not in [str, unicode] or len(nombre) < 2:
        errores.append('Nombre del participante {0:d} es inválido.'.format(pos))

    if type(apellido) not in [str, unicode] or len(apellido) < 2:
        errores.append('Apellido del participante {0:d} es inválido.'.format(pos))

    return errores


def _validar_participantes(acta):
    errores = []

    participantes = acta.get('participantes', [])

    if type(participantes) != list or not (PARTICIPANTES_MIN <= len(participantes) <= PARTICIPANTES_MAX):
        errores.append('Error en el formato de los participantes.')
        return errores

    for i, participante in enumerate(participantes):
        errores += _validar_participante(participante, i + 1)

    if len(errores) > 0:
        return errores

    ruts_participantes = [p['rut'] for p in participantes]

    # Ruts diferentes
    ruts = set(ruts_participantes)
    if not (PARTICIPANTES_MIN <= len(ruts) <= PARTICIPANTES_MAX):
        return ['Existen RUTs repetidos']

    # Nombres diferentes
    nombres = set(
        (p['nombre'].lower(), p['apellido'].lower(), ) for p in participantes
    )
    if not (PARTICIPANTES_MIN <= len(nombres) <= PARTICIPANTES_MAX):
        return ['Existen nombres repetidos']

    # Verificar que los participantes no hayan enviado una acta antes
    participantes_en_db = User.objects.filter(username__in=list(ruts))

    if len(participantes_en_db) > 0:
        for participante in participantes_en_db:
            errores.append('El RUT {0:s} ya participó del proceso.'.format(participante.username))

    return errores


def _validar_cedula_participantes(acta):
    errores = []

    participantes = acta.get('participantes', [])

    for participante in participantes:
        errores += verificar_cedula(participante.get('rut'), participante.get('serie_cedula'))

    return errores


def _validar_items(acta):
    errores = []

    # TODO: Validar todos los items por DB

    for group in acta['itemsGroups']:
        for i, item in enumerate(group['items']):
            acta_item = Item.objects.filter(pk=item.get('pk'))

            if len(acta_item) != 1 or acta_item[0].nombre != item.get('nombre'):
                errores.append(
                    'Existen errores de validación en ítem {0:s} del grupo {1:s}.'.format(
                        item.get('nombre').encode('utf-8'),
                        group.get('nombre').encode('utf-8')
                    )
                )

            if item.get('categoria') not in ['-1', '0', '1']:
                errores.append(
                    'No se ha seleccionado la categoría del ítem {0:s}, del grupo {1:s}.'.format(
                        item.get('nombre').encode('utf-8'),
                        group.get('nombre').encode('utf-8')
                    )
                )

    return errores


def _crear_usuario(datos_usuario):
    usuario = User(username=datos_usuario['rut'])
    usuario.first_name = datos_usuario['nombre']
    usuario.last_name = datos_usuario['apellido']
    usuario.save()
    return usuario


def _guardar_acta(datos_acta):
    acta = Acta(
        comuna=Comuna.objects.get(pk=datos_acta['geo']['comuna']),
        memoria_historica=datos_acta.get('memoria'),
        fecha=timezone.now(),
    )

    acta.save()

    for p in datos_acta['participantes']:
        acta.participantes.add(_crear_usuario(p))

    acta.save()

    for group in datos_acta['itemsGroups']:
        for i in group['items']:
            item = Item.objects.get(pk=i['pk'])
            acta_item = ActaRespuestaItem(
                acta=acta,
                item=item,
                categoria=i['categoria'],
                fundamento=i.get('fundamento')
            )
            acta_item.save()


def _validar(request):
    if request.method != 'POST':
        return ['Request inválido.']

    acta = request.body.decode('utf-8')
    acta = json.loads(acta)

    for func_val in [_validar_datos_geograficos, _validar_participantes, _validar_items]:
        errores = func_val(acta)
        if len(errores) > 0:
            return (acta, errores,)

    return (acta, [],)


@transaction.atomic
def subir_validar(request):
    acta, errores = _validar(request)

    if len(errores) > 0:
        return JsonResponse({'status': 'error', 'mensajes': errores}, status=400)

    return JsonResponse({'status': 'success', 'mensajes': ['El acta ha sido validada exitosamente.']})


@transaction.atomic
def subir_confirmar(request):
    acta, errores = _validar(request)

    if len(errores) > 0:
        return JsonResponse({'status': 'error', 'mensajes': errores}, status=400)

    errores = _validar_cedula_participantes(acta)

    if len(errores) == 0:
        _guardar_acta(acta)
        return JsonResponse({'status': 'success', 'mensajes': ['El acta ha sido ingresada exitosamente.']})

    return JsonResponse({'status': 'error', 'mensajes': errores}, status=400)
