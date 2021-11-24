#!/usr/bin/env python3
from selenium import webdriver
import datetime
import argparse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

hora_default = "20:00"  # hora por defecto a reservar

print("Bot reserva SmartFit, por https://deivid.xyz")
print("********************************************")
parser = argparse.ArgumentParser(description="Bot para reservar hora en SmartFit (Chile)",
                                 epilog='https://deivid.xyz/')
parser.add_argument('--usuario', type=str, help='''Usuario de SmartFit (RUT). Requerido para reservar.''',
                    required=True)
parser.add_argument('--password', type=str, help='''Contraseña de SmartFit. Requerido para reservar.''',
                    required=True)
parser.add_argument('--fecha', type=str, help='''Fecha para reservar hora.\n
Formato debe ser AAAA-MM-DD. Si no se incluye fecha, se utilizará la fecha de hoy.''', required=False)
parser.add_argument("--horizonte", type=int, help="""Horizonte de cita para considerar a partir de la fecha. 
Ejemplo: Si valor es 1, se considera la fecha de reserva para el díá de mañana, asumiendo la fecha de hoy como referencia. 
Valor debe estar entre 0 y 6.""", required=False)
parser.add_argument('--hora', type=str, help='''Hora para reserva, formato HH:MM (24 hrs). 
Si no se especifica, se utilizará 20:00.''', default=hora_default, required=False)
parser.add_argument('--headless', action='store_true',
                    help="Si se especifica, inicia Chrome en modo headless (sin ventana).", required=False)
parser.add_argument('--dias_allowed', nargs='*', help="""Dias de la semana para los que pediré hora.
Valores posibles: lun, mar, mie, jue, vie, sab, dom. Varios días se pueden escribir separados por espacio.""", required=False)

p = parser.parse_args()

if p.fecha is None:
    fecha_input = datetime.datetime.today()  # considero la fecha de hoy
else:
    fecha_input = datetime.date(int(p.fecha[0:4]), int(p.fecha[5:7]), int(p.fecha[8:10]))  # armo fecha a partir de arg

if p.horizonte is not None:
    horizonte = datetime.timedelta(days=p.horizonte)
else:
    horizonte = datetime.timedelta(days=0)

dia_busqueda = fecha_input + horizonte
dia_busqueda_diasem = dia_busqueda.weekday()

dias_allowed = []
if p.dias_allowed is not None:
    for dia in p.dias_allowed:
        if dia == 'lun':
            dias_allowed.append(0)
        elif dia == 'mar':
            dias_allowed.append(1)
        elif dia == 'mie':
            dias_allowed.append(2)
        elif dia == 'jue':
            dias_allowed.append(3)
        elif dia == 'vie':
            dias_allowed.append(4)
        elif dia == 'sab':
            dias_allowed.append(5)
        elif dia == 'dom':
            dias_allowed.append(6)
        else:
            continue

if dia_busqueda_diasem not in dias_allowed and dias_allowed.__len__()>0:
    print('No se ejecutó proceso puesto que la el día de la semana fue excluido.')
    print('Saliendo ...')
else:
    dia_busqueda_str = dia_busqueda.strftime("%Y-%m-%d")
    usr = p.usuario
    passwd = p.password

    hora_solicitada = p.hora

    option = webdriver.ChromeOptions()
    chrome_prefs = {}
    option.experimental_options["prefs"] = chrome_prefs
    if p.headless is True:
        option.add_argument("--headless") # descomentar cuando no se quiera ver la salida

    # no cargaremos imagenes del sitio
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    driver = webdriver.Chrome(options=option)

    # url tu espacio
    login_url = 'https://smartfit.cl/person_sessions/new'

    # login stuff
    usr_xpath = "/html//input[@id='login']"
    passwd_xpath = "/html//input[@id='person_session_password']"
    login_btn = "/html//input[@id='s_login']"

    try:
        driver.get(login_url)  # ingreso al sitio

        # logueo
        driver.find_element(By.XPATH, usr_xpath).send_keys(usr)
        driver.find_element(By.XPATH, passwd_xpath).send_keys(passwd)
        driver.find_element(By.XPATH, login_btn).click()

        # espera login

        xpath_reservas = "//a[contains(@href, 'https://reservas.smartfit.cl/session/remote_sign_in?')]"

        try:
            wait_menu = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, xpath_reservas))
            )

        finally:
            link_reserva = driver.find_elements(By.XPATH, xpath_reservas)[0].get_attribute('href')
            driver.get(link_reserva)

        # una vez ya logueado, la url de consultas se compone del dia y la url base de abajo
        driver.get('https://reservas.smartfit.cl/klasses?date={}'.format(dia_busqueda_str))

        # xpath del selector de horas
        hora_xpath = "//div[contains(@class, 'Card__item__info')]"  # contiene la hora del bloque
        boton_reserva_xpath = "//div[contains(@class, 'Card__item__column--button')]"  # botón para reservar hora
        bloques_horarios_xpath = "/html/body/div[2]/main/div[5]/div"  # fila de cada elemento donde se ubica hora / botón

        bloques_horarios = driver.find_elements(By.XPATH, bloques_horarios_xpath).__len__()  # veo cuantos bloques hay

        lista_bloques = []  # acá dejaré los bloques horarios disponibles

        for i in range(1, bloques_horarios + 1):
            xpath_bloque = "/html/body/div[2]/main/div[5]/div[{}]".format(i)  # con el ciclo voy fila x fila
            hora = driver.find_element(By.XPATH, xpath_bloque + hora_xpath).text  # busco la hora de cada fila que haya y la almaceno
            try:  # debo ver si para cada fila, el botón para reservar está habilitado
                revision_btn = driver.find_element(By.XPATH, xpath_bloque + "//div[contains(@class, 'Card__item__column--button')]/a")
            except NoSuchElementException:  # si el boton no tiene un link (no habilitado), es un horario agotado!
                revision_btn = None  # mi revisión será none

            if revision_btn is None:
                estado = False  # el estado de esa reserva será False cuando el horario no se pueda reservar
            else:
                estado = True  # True cuando el bloque este disponible

            # almaceno la info en un diccionario elem

            elem = {
                "horafecha": hora,
                "hora": hora[6:],
                "estado": estado,
                "id": i
            }

            # almaceno diccionario en lista
            lista_bloques.append(elem)
        existe_hora = 0
        print("")
        for hora in lista_bloques:
            if hora['estado']:  # si el estado es true
                print("Hora disponible: {}".format(hora["horafecha"]))
                if hora["hora"] == hora_solicitada:  # si la hora disponible es igual a la solicitada, reservo
                    existe_hora = 1
                    driver.find_element(By.XPATH, "/html/body/div[2]/main/div[5]/div[{}]".format(hora["id"]) +
                                        "//div[contains(@class, 'Card__item__column--button')]").click() # pincho la reserva
                    try:
                        alerta_reserva = driver.find_element(By.XPATH,
                                                             "//*[@id='flash-message']/div[contains(@class, 'Message__item Message__item--alert')]").text  # mensaje de no se puede
                        if 'No es posible' in alerta_reserva:
                            print("{}. Prueba más tarde.".format(alerta_reserva))
                        else:
                            print('Hora reservada! {} a las {}'.format(dia_busqueda_str, hora_solicitada))
                        break
                    except NoSuchElementException:
                        print('Hora reservada! {} a las {}'.format(dia_busqueda_str, hora_solicitada))
                        break
                    # TODO: hay que verificar el flujo cuando la reserva se ejecuta (revisar el mensaje de reserva ok)
                    # Esto debe esperar puesto que ya reservé hora :(
        print("")
        if existe_hora != 1:
            print("No se encontró hora solicitada disponible ({} {}).".format(dia_busqueda_str, hora_solicitada))
            print("Puedes probar otro día, o bien, pedir otra hora disponible del listado.")
        driver.close()

    except KeyboardInterrupt:
        print("Saliendo ...!")
        driver.close()