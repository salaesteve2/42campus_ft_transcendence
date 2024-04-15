# coding=utf-8
   
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .models import Torneo, FaseTorneo
from .forms import TorneoForm
from general.views import  activate_language
from general.models import UserSettings
from base.forms import UserSettingsForm
from web3 import Web3
from web3.contract import Contract
from web3.auto import w3
from eth_account import Account
from django.http import JsonResponse
import datetime
import random
import re
from django.contrib import messages

contract_abi = [
    {
        "constant": False,
        "inputs": [
            {"name": "_login", "type": "string"},
            {"name": "_score", "type": "uint32"}
        ],
        "name": "doUser",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_login", "type": "string"}],
        "name": "getUserScore",
        "outputs": [{"name": "", "type": "uint32"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# ESTO ES PARA ESCRIBIR; no gastar ETH pls
def agregar_o_actualizar_usuario(login, score):
	
	w3 = Web3(Web3.HTTPProvider('https://rpc2.sepolia.org'))

	private_key = "7c..."

	cuenta = w3.eth.account.from_key(private_key).address

	w3.eth.default_account = w3.eth.account.from_key(private_key).address

	contract = w3.eth.contract(address='0x63...', abi=contract_abi)

	nonce = w3.eth.get_transaction_count(w3.eth.default_account)

	txn_dict = contract.functions.doUser(login, score).build_transaction({
		'from': cuenta,
        'value': 0,
        'gas': 1000000,
        'gasPrice': w3.to_wei('50', 'gwei'),  # Reemplaza '50' con el precio de gas deseado en gwei
        'nonce': nonce,
    })

	signed_txn = w3.eth.account.sign_transaction(txn_dict, private_key=private_key)
	tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
	# Esta ultima no es necesaria, pero la consideran una buena práctica (pero no la he probado aun)
	# w3.eth.waitForTransactionReceipt(tx_hash)

def obtener_puntaje_usuario(login):
    # Llamar a la función getUserScore del contrato inteligente
    puntaje = contract.functions.getUserScore(login).call()
    return puntaje

def torneos_inscripcion_list(request):
	torneos_mantenimiento2()
	activate_language(request)
	if not request.user.is_authenticated:
		return redirect('home')
	t = datetime.datetime.now()
	torneos2 = []
	torneo2 = {}
	torneos = Torneo.objects.all().filter(comienzo_inscripcion__lt=t, fin_inscripcion__gt=t)
	for torneo in torneos:
		idTorneo = torneo.id
		fasesTorneo = FaseTorneo.objects.filter(torneo=idTorneo).order_by('fase')
		for faseTorneo in fasesTorneo:
			lpr1 = faseTorneo.lista_partidos_resultados
			lpr2 = re.sub( "{[0-9]+}", "", lpr1)
			faseTorneo.lista_partidos_resultados = lpr2
		torneo2 = {}
		torneo2['copy'] = torneo
		torneo2['fases'] = fasesTorneo
		jugadores_actualizados = []
		for jugador in torneo.jugadores.all():
			user_settings, created = UserSettings.objects.get_or_create(user=jugador)
			alias = user_settings.alias
			if alias and alias != "":
				jugador_con_alias = jugador
				jugador_con_alias.alias = alias
				jugadores_actualizados.append(jugador_con_alias)
			else:
				jugadores_actualizados.append(jugador)
    # Asignar la lista de jugadores actualizados a torneo2
		torneo2['jugadores'] = jugadores_actualizados
		torneos2.append(torneo2)
	context = {'torneos': torneos, 'user': request.user, 'alias': torneos2}
	# AQui mismo hago la prueba de lectura; se activa clicando en inscripcion torneos y printea en el CLI de Django
	# puntos = obtener_puntaje_usuario("jaja")
	# print("\npuntos de jaja:\n")
	# print(puntos)
    	# # Llamar a las funciones para ESCRIBIR del contrato inteligente
	# agregar_o_actualizar_usuario("MrFunciona", 3)
	return render(request, 'torneos/torneos_inscripcion_t.html', context)

def update_alias(request):
	if request.method == 'POST':
			aa = request.POST.get('alias')
			if aa == "":
				user = User.objects.get(username=request.user.username)
				user_settings, created = UserSettings.objects.get_or_create(user=user)
				user_settings.alias = aa
				user_settings.save()
				return JsonResponse({'success': True, 'new_alias': aa})
			elif not re.match("^[a-zA-Z0-9]+$", aa) or len(aa) > 50:
            # Return JSON with error message
				return JsonResponse({'success': False, 'error': "El alias solo puede contener letras y números, y no puede tener más de 50 caracteres."})
			else:
				user = User.objects.get(username=request.user.username)
				user_settings, created = UserSettings.objects.get_or_create(user=user)
				user_settings.alias = aa
				user_settings.save()
            # Return success JSON
				return JsonResponse({'success': True, 'new_alias': aa})
	return JsonResponse({'success': False})
	#return redirect('torneos_inscripcion_list')

def torneos_inscripcion(request):
	activate_language(request)
	if not request.user.is_authenticated:
		return redirect('home')	
	idTorneo = int(request.GET.get('idTorneo'))
	idUser = int(request.GET.get('idUser'))
	torneo = Torneo.objects.get(id=idTorneo)
	user = User.objects.get(id=idUser)
	if torneo.jugadores.filter(id=idUser).exists():
		torneo.jugadores.remove(user)
	else:
		torneo.jugadores.add(user)
	torneo.save()
	torneos_mantenimiento2()
	t = datetime.datetime.now()
	torneos2 = []
	torneo2 = {}
	torneos = Torneo.objects.all().filter(comienzo_inscripcion__lt=t, fin_inscripcion__gt=t)
	for torneo in torneos:
		idTorneow = torneo.id
		fasesTorneo = FaseTorneo.objects.filter(torneo=idTorneow).order_by('fase')
		for faseTorneo in fasesTorneo:
			lpr1 = faseTorneo.lista_partidos_resultados
			lpr2 = re.sub( "{[0-9]+}", "", lpr1)
			faseTorneo.lista_partidos_resultados = lpr2
		torneo2 = {}
		torneo2['copy'] = torneo
		torneo2['fases'] = fasesTorneo
		jugadores_actualizados = []
		for jugador in torneo.jugadores.all():
			user_settings, created = UserSettings.objects.get_or_create(user=jugador)
			alias = user_settings.alias
			if alias and alias != "":
				jugador_con_alias = jugador
				jugador_con_alias.alias = alias
				jugadores_actualizados.append(jugador_con_alias)
			else:
            # Si no hay alias definido, mantener el jugador original
				jugadores_actualizados.append(jugador)
    # Asignar la lista de jugadores actualizados a torneo2
		torneo2['jugadores'] = jugadores_actualizados
		torneos2.append(torneo2)
	context = {'torneos': torneos, 'user': request.user, 'alias': torneos2}
	form_html = render(request, 'torneos/torneos_inscripcion_t.html', context).content.decode()
	return JsonResponse({'redirect_url': '/', 'form_html': form_html})

def torneos_admin(request):
	torneos_mantenimiento2()
	if not request.user.is_authenticated:
		return redirect('home')	
	activate_language(request)
	if not request.user.is_staff: 
		return
	torneos = Torneo.objects.all().order_by('-comienzo_partidos')
	#torneos = Torneo.objects.filter(comienzo_inscripcion__lt=t, fin_inscripcion__gt=t).order_by('-comienzo_partidos')
	context = {'torneos': torneos, }
	return render(request, 'torneos/torneos_admin_t.html', context)
		
def torneos_delete(request):
	if not request.user.is_staff: 
		return
	idTorneo = request.GET.get('idTorneo')
	torneo = Torneo.objects.get(id=idTorneo)
	torneo.delete()
	#torneos = Torneo.objects.filter(comienzo_inscripcion__lt=t, fin_inscripcion__gt=t).order_by('-comienzo_partidos')
	redirect_url2 = 'torneos_admin'
	return JsonResponse({'redirect_url': '/', 'redec': redirect_url2})
	return JsonResponse({'redirect_url': redirect_url})
	#return render(request, 'torneos/torneos_admin_t.html', context)
	
def torneos_edit(request):
	activate_language(request)
	if not request.user.is_staff: 
		return
	if request.method == 'POST':
		#print("edición terminada -> hay que salvar (modificar o insertar nuevo)")
		idTorneo = int(request.POST.get('idTorneo'))
		form = TorneoForm(request.POST) # datos procedentes del form
		if form.is_valid():
			cd = form.cleaned_data # datos procedentes del form
			if idTorneo != -1: # modify
				torneo = Torneo.objects.get(id=idTorneo) # get torneo
				torneo.nombre = cd['nombre']
				torneo.comienzo_inscripcion = cd['comienzo_inscripcion']
				torneo.fin_inscripcion = cd['fin_inscripcion']
				torneo.comienzo_partidos = cd['comienzo_partidos']
				torneo.minutos_duracion_maxima_partidos = cd['minutos_duracion_maxima_partidos']
				torneo.minutos_entre_partidos = cd['minutos_entre_partidos']
				#print("salva modificación")
				torneo.save()
			else: # new
				torneo = Torneo() # new torneo
				torneo.setDateTimes()
				#print(torneo)
				torneo.nombre = cd['nombre']
				torneo.comienzo_inscripcion = cd['comienzo_inscripcion']
				torneo.fin_inscripcion = cd['fin_inscripcion']
				torneo.comienzo_partidos = cd['comienzo_partidos']
				torneo.minutos_duracion_maxima_partidos = cd['minutos_duracion_maxima_partidos']
				torneo.minutos_entre_partidos = cd['minutos_entre_partidos']
				#print("salva nuevo")
				torneo = Torneo(**cd)
				torneo.save()
				form_data_serializable = {
					'nombre': cd['nombre'],
					'comienzo_inscripcion': cd['comienzo_inscripcion'].isoformat() if cd['comienzo_inscripcion'] else None,
					'fin_inscripcion': cd['fin_inscripcion'].isoformat() if cd['fin_inscripcion'] else None,
					'comienzo_partidos': cd['comienzo_partidos'].isoformat() if cd['comienzo_partidos'] else None,
					'minutos_duracion_maxima_partidos': cd['minutos_duracion_maxima_partidos'],
					'minutos_entre_partidos': cd['minutos_entre_partidos']
				}
				
				# Guardar los datos del formulario en la sesión antes de la redirección
				request.session['form5_data'] = form_data_serializable
			form_html = render(request, 'torneos/torneos_admin_t.html', {'form5': form}).content.decode()
			return JsonResponse({'redirect_url': '/', 'form_html': form_html})
			#return render(request, 'singlepage/index.html', {'form2': form})
	else:
		# crear el html para editar (comienzo de edición)
		idTorneo = request.GET.get('idTorneo')
		if (idTorneo):  # modificar
			#print("html para modificar")
			idTorneo = int(idTorneo)
			torneo = Torneo.objects.get(id=idTorneo)
			dd = {
				'nombre': torneo.nombre, 
				'comienzo_inscripcion': torneo.comienzo_inscripcion,
				'fin_inscripcion': torneo.fin_inscripcion,
				'comienzo_partidos': torneo.comienzo_partidos,
				'minutos_duracion_maxima_partidos': torneo.minutos_duracion_maxima_partidos,
				'minutos_entre_partidos': torneo.minutos_entre_partidos
			}
			form = TorneoForm(initial=dd)
			form_html = render(request, 'torneos/torneos_edit_t.html', {'form': form, 'idTorneo': idTorneo}).content.decode()
			return JsonResponse({'redirect_url': '/', 'form_html': form_html})
		else: # nuevo
			#print("html para añadir nuevo")
			idTorneo = -1 
			torneo = Torneo() # vacío
			torneo.setDateTimes()
			dd = {
				'nombre': torneo.nombre, 
				'comienzo_inscripcion': torneo.comienzo_inscripcion,
				'fin_inscripcion': torneo.fin_inscripcion,
				'comienzo_partidos': torneo.comienzo_partidos,
				'minutos_duracion_maxima_partidos': torneo.minutos_duracion_maxima_partidos,
				'minutos_entre_partidos': torneo.minutos_entre_partidos
			}
			form = TorneoForm(initial=dd) 
			return render(request, 'torneos/torneos_edit_t.html', {'form': form, 'idTorneo': idTorneo})

# Python program to sort a list of
# tuples by the second Item using sort() 
# Function to sort the list by second item of tuple
def fSortListOfTuple(listOfTuple): 
    # reverse = None (Sorts in Ascending order) 
    # key is set to sort using second element of 
    # sublist lambda has been used 
    listOfTuple.sort(key = lambda x: x[1]) 
    return listOfTuple

def torneos_mantenimiento(request):
	torneos_mantenimiento2()
	# aquí se pueden hacer pruebas
	return redirect('home')

def torneos_mantenimiento2():
	# esto hay que ejecutarlo periodicamente
	# lo mejor es repetir esto en todo lo que se haga dentro de torneos
	# se intentó meter en home pero da errores 
	# si se presenta un solo jugador el resultado lo resuelve el propio partido arranque_torneo
	print("mantenimiento")
	t = datetime.datetime.now()
	torneos = Torneo.objects.filter(fin_inscripcion__lt=t, terminado=False)
	for torneo in torneos:
		#print("mantenimiento " + torneo.nombre)
		if torneo.fase_actual != 0: # la fase 0 no se puede cerrar (no tiene partidos)
			ok = cierre_fase(torneo)
			if not ok:
				continue
		# si logra cerrar la fase intenta poner una fase nueva
		fase_actual = torneo.fase_actual
		fase_calculada = torneo.getFase()
		#print("fase calculada = " + str(fase_calculada))
		if fase_calculada > fase_actual:
			#print('mantenimiento de torneo ' + torneo.nombre)
			torneo_nuevaFase(torneo)

# para cuando no se han presentado ninguno de los jugadores
def cierre_fase(torneo): # probar ???
	#print("cierre de fase comienzo")
	fase_actual = torneo.fase_actual
	if fase_actual == 0:
		return False
	comienzo_partidos = torneo.comienzo_partidos
	minutos_duracion_maxima_partidos = torneo.minutos_duracion_maxima_partidos + 1 # se suma 1 min como margen
	mdmp = datetime.timedelta(minutes=minutos_duracion_maxima_partidos) 
	minutos_entre_partidos = torneo.minutos_entre_partidos
	mep = datetime.timedelta(minutes=minutos_entre_partidos)
	comienzo_partidos_fase = comienzo_partidos + mep * (fase_actual - 1)
	terminacion_partidos_fase = comienzo_partidos_fase + mdmp
	t = datetime.datetime.now()
	#print("fecha-hora de terminacion de partidos " + str(terminacion_partidos_fase))
	if t < terminacion_partidos_fase:
		return False
	faseTorneo = FaseTorneo.objects.get(torneo=torneo, fase=fase_actual)		
	lpr = faseTorneo.lista_partidos_resultados
	faseTorneo.lista_partidos_resultados = re.sub( "{[0-9]+}", "-", lpr)
	faseTorneo.save()
	#print("cierre de fase fin")
	return True

def torneo_nuevaFase(torneo):
	fase_actual = torneo.fase_actual
	#print("nueva fase")
	if fase_actual == 0:
		jugadores = torneo.jugadores
	else:
		faseTorneo = FaseTorneo.objects.get(torneo=torneo, fase=fase_actual)
		jugadores = faseTorneo.ganadores
		lista_partidos_resultados = faseTorneo.lista_partidos_resultados
		#print(lista_partidos_resultados)
		if "{" in lista_partidos_resultados:
			return # sin acabar la fase actual
	list = []
	for jugador in jugadores.all():
		tup2 = ( jugador.id, random.random() ) # orden aleatorio - tupla de 2 ( id, número_aleatorio)
		list.append(tup2)
	if len(list) == 0:
		print('no quedan jugadores')
		torneo.terminado = True
		torneo.save()
		return
	if len(list) == 1:
		print('hay un ganador')
		torneo.terminado = True
		torneo.save()
		# # DESCOMENTAR PARA ESCRIBIR AL BLOCKCHAIN
		# ganador_id = list[0][0]
    	# login = User.objects.get(id=ganador_id).**login_field**
    	# score = User.objects.get(id=ganador_id).**score_field**
    	# # Llamar a las funciones del contrato inteligente
    	# agregar_o_actualizar_usuario(login, score)
		return
	fSortListOfTuple(list)
	#print(list)
	fase_actual += 1
	faseTorneo = FaseTorneo() # nueva fase
	faseTorneo.torneo = torneo
	faseTorneo.fase = fase_actual
	# Generación de strings
	pasaUltimoJugador = False
	n = 0
	lp = "[ "
	lista_jugadores = ""
	for jn in list:
		j = jn[0]
		if lista_jugadores != "":
			lista_jugadores += ","
		lista_jugadores += str(j)
		user = User.objects.get(id=j)
		if n % 2 == 0:
			if n != 0:
				lp += ", "
			lp  += "( " + user.username + " {" +  str(user.id) + "}"
		else:
			lp += ", " + user.username + " {" + str(user.id) + "} )"
		n += 1	
	if n % 2 == 1:
		lp += " )"
		pasaUltimoJugador = True
	lp += " ]"
	#print(lp)
	lp1 = lp
	if pasaUltimoJugador:
		s1 = "{" +  str(user.id) + "}"
		lp1 = lp.replace(s1, "*")
		faseTorneo.ganadores.add(user)	
	lp2 = re.sub( "{[0-9]+}", "", lp)
	faseTorneo.lista_jugadores = lista_jugadores
	faseTorneo.lista_partidos = lp2
	faseTorneo.lista_partidos_resultados = lp1
	faseTorneo.save()
	torneo.fase_actual = fase_actual
	torneo.save()

def torneos_info_list(request):
	torneos_mantenimiento2()
	activate_language(request)
	if not request.user.is_authenticated:
		return redirect('home')
	torneos2 = []
	torneo2 = {}
	torneos = Torneo.objects.all().order_by('-comienzo_partidos')
	for torneo in torneos:
		idTorneo = torneo.id
		fasesTorneo = FaseTorneo.objects.filter(torneo=idTorneo).order_by('fase')
		for faseTorneo in fasesTorneo:
			lpr1 = faseTorneo.lista_partidos_resultados
			lpr2 = re.sub( "{[0-9]+}", "", lpr1)
			faseTorneo.lista_partidos_resultados = lpr2
		torneo2 = {}
		torneo2['copy'] = torneo
		torneo2['fases'] = fasesTorneo
		jugadores_actualizados = []
		for jugador in torneo.jugadores.all():
			user_settings, created = UserSettings.objects.get_or_create(user=jugador)
			alias = user_settings.alias
			if alias and alias != "":
				jugador_con_alias = jugador
				jugador_con_alias.alias = alias
				jugadores_actualizados.append(jugador_con_alias)
			else:
            # Si no hay alias definido, mantener el jugador original
				jugadores_actualizados.append(jugador)
    # Asignar la lista de jugadores actualizados a torneo2
		torneo2['jugadores'] = jugadores_actualizados
		torneos2.append(torneo2)
	return render(request, 'torneos/torneos_info_t.html',  {'torneos': torneos2})

"""
def torneo_pasa(idTorneo, fase, idJugador): # no se usa solo para pruebas
	try:
		faseTorneo = FaseTorneo.objects.get(torneo=idTorneo, fase=fase)
	except FaseTorneo.DoesNotExist:
		return
	user = User.objects.get(id=idJugador)
	faseTorneo.ganadores.add(user)
	s1 = "{" +  str(user.id) + "}"
	lpr =	faseTorneo.lista_partidos_resultados
	lpr2 = lpr.replace(s1, "*")
	faseTorneo.lista_partidos_resultados = lpr2
	faseTorneo.save()
"""

def strToListOfInt(str):
	if str=="":
		return []
	list = str.split(",")
	result = []
	for s in list:
		error = False
		try:
			i = int(s)
		except ValueError:
			error = True
		if error:
			continue
		result.append(i)
	return result
	
def proximos_torneos(idJugador):
	torneos_mantenimiento2() # esto se llama desde home
	result = []
	torneos = Torneo.objects.filter(terminado=False)
	user = User.objects.get(id=idJugador)
	t = datetime.datetime.now()
	for torneo in torneos:
		mep = datetime.timedelta(minutes=torneo.minutos_entre_partidos)
		comienzo_partidos = torneo.comienzo_partidos
		fase_actual = torneo.fase_actual		
		ok = False
		if fase_actual == 0:
			jugadores = torneo.jugadores
			if jugadores.filter(id=idJugador).exists():
				ok = True
			comienzo = comienzo_partidos
		else:
			faseTorneo = FaseTorneo.objects.get(torneo=torneo, fase=fase_actual)
			lista_jugadores = strToListOfInt(faseTorneo.lista_jugadores)
			if idJugador in lista_jugadores:
				ok = True
			comienzo = comienzo_partidos + (torneo.fase_actual - 1) * mep
		if t > comienzo or not ok:
			continue
		date_time = comienzo.strftime("%Y-%m-%d %H:%M:%S")
		result.append(date_time) 
	result.sort()
	#print(result)
	return result

def torneo_jugar(idJugador):
	torneos = Torneo.objects.filter(terminado=False)
	user = User.objects.get(id=idJugador)
	for torneo in torneos:
		if not torneo.esHoraDeEmpezar():
			continue
		fase_actual = torneo.fase_actual
		if fase_actual == 0:
			continue
		faseTorneo = FaseTorneo.objects.get(torneo=torneo, fase=fase_actual)
		lpr = faseTorneo.lista_partidos_resultados
		lista_jugadores = strToListOfInt(faseTorneo.lista_jugadores)
		pJugador1 = -1
		pJugador2 = -1
		n = 0
		iLen = len(lista_jugadores)
		for idJ in lista_jugadores:
			# la posición es importante poque par indica que es jugador1 (izq) e impar que es jugador2 (derecha)
			if idJ == idJugador:
				if n % 2 == 0:
					pJugador1 = n
					if n+1 < iLen:
						pJugador2 = n+1
				else:
					pJugador1 = n-1
					pJugador2 = n
				break
			n += 1
		if pJugador1 == -1:
			continue
		idJugador1 = lista_jugadores[pJugador1]
		if pJugador2 == -1:
			continue
		idJugador2 = lista_jugadores[pJugador2]
		margen = datetime.timedelta(seconds=30)
		mep = datetime.timedelta(minutes=torneo.minutos_entre_partidos)
		dmp = datetime.timedelta(minutes=torneo.minutos_duracion_maxima_partidos)
		mepPn = (torneo.fase_actual - 1) * mep
		torneoFase_comienzo_partidos = torneo.comienzo_partidos + mepPn
		limiteTiempoTorneo = torneoFase_comienzo_partidos + dmp
		limiteTiempoConUnJugador = torneoFase_comienzo_partidos + margen
		result = { 'ok': True, 'idTorneo': torneo.id, 'fase': fase_actual, 
						'idJugador1': idJugador1, 'idJugador2': idJugador2,
						'limiteTiempoTorneo' : limiteTiempoTorneo,
						'limiteTiempoConUnJugador': limiteTiempoConUnJugador
					}
		return result
	return  { 'ok': False }
	
def torneo_result(idTorneo, fase, idJugador1, idJugador2, puntos1, puntos2):
	try:
		faseTorneo = FaseTorneo.objects.get(torneo=idTorneo, fase=fase)
	except FaseTorneo.DoesNotExist:
		return
	#print("torneo_result")
	lista_jugadores = strToListOfInt(faseTorneo.lista_jugadores)
	n = 0
	pj1 = -1
	pj2 = -1
	for idJ in lista_jugadores:
		if idJ == idJugador1:
			pj1 = n
		if idJ == idJugador2:
			pj2 = n
		n+=1
	if pj1 == -1:
		return
	if pj2 == -1:
		return
	dif = abs(pj1 - pj2)
	if dif != 1:
		return
	s1 = "{" + str(idJugador1) +  "}"
	s2 = "{" + str(idJugador2) +  "}"
	lpr = faseTorneo.lista_partidos_resultados
	if puntos1 == -1:
		p1 = " -"
	else:
		p1 = str(puntos1)
	if puntos2 == -1:
		p2 = " -"
	else:
		p2 = str(puntos2)		
	if puntos1 >= puntos2: # en caso de empate a puntos gana el jugaodor1
		m1 = " *"
		m2 = ""
		user1 = User.objects.get(id=idJugador1)
		#print("ganador 1 "+ user1.username)
		faseTorneo.ganadores.add(user1)
	else:
		m1 = ""
		m2 = " *"
		user2 = User.objects.get(id=idJugador2)
		#print("ganador 2 "+ user2.username)
		faseTorneo.ganadores.add(user2)
	r1 = p1 + m1
	r2 = p2 + m2
	lpr2 = lpr.replace(s1, r1).replace(s2, r2)
	#print(lpr2)
	faseTorneo.lista_partidos_resultados = lpr2
	faseTorneo.save()
	#print("torneo_result fin")
	return

