# bot_smartfit
## Bot para reservar horas en SmartFit (Chile)

Programa para revisar horas en SmartFit Chile y pedir hora de manera automática. Hecho con Python y Selenium.

---

## Aviso Importante
El presente proyecto no tiene relación alguna con el sitio smartfit.cl ni tampoco con sus creadores/administradores.
El autor se desliga de cualquier responsabilidad derivada del uso del presente código.

## Requisitos

- Python 3.6 o superior.
- Selenium-Python (```pip install selenium```)
- Google Chrome / Chromium y ChromeDriver.

El código fue programado usando el IDE PyCharm 2021.2.3 y testeado en Linux (OpenSuse Tumbleweed). Probablemente el código pueda funcionar sin modificaciones en 
OS X. Usuarios de Windows pueden testearlo en WSL o bien con distribuciones de Python como Anaconda, o la instalable desde la Microsoft Store.

También este script está desarrollado para usuarios de plan Smart (no incluye extras de plan Black, como elegir sucursal).

## Uso

```
Bot reserva SmartFit, por https://deivid.xyz
********************************************
usage: smartfit_bot.py [-h] --usuario USUARIO --password PASSWORD [--fecha FECHA] [--horizonte HORIZONTE] [--hora HORA] [--headless] [--dias_allowed [DIAS_ALLOWED [DIAS_ALLOWED ...]]]

Bot para reservar hora en SmartFit (Chile)

optional arguments:
  -h, --help            show this help message and exit
  --usuario USUARIO     Usuario de SmartFit (RUT). Requerido para reservar.
  --password PASSWORD   Contraseña de SmartFit. Requerido para reservar.
  --fecha FECHA         Fecha para reservar hora. Formato debe ser AAAA-MM-DD. Si no se incluye fecha, se utilizará la fecha de hoy.
  --horizonte HORIZONTE
                        Horizonte de cita para considerar a partir de la fecha. Ejemplo: Si valor es 1, se considera la fecha de reserva para el díá de mañana, asumiendo la fecha de hoy como referencia. Valor debe estar entre 0 y 6.
  --hora HORA           Hora para reserva, formato HH:MM (24 hrs). Si no se especifica, se utilizará 20:00.
  --headless            Si se especifica, inicia Chrome en modo headless (sin ventana).
  --dias_allowed [DIAS_ALLOWED [DIAS_ALLOWED ...]]
                        Dias de la semana para los que pediré hora. Valores posibles: lun, mar, mie, jue, vie, sab, dom. Varios días se pueden escribir separados por espacio.

```

## Ejemplo de uso

Acá se muestra un ejemplo para pedir hora a las 21:00 horas de mañana.

```
deivid@deivid-pc:~> ./smartfit_bot.py --usuario <rut> --password <contraseña> --horizonte 1 --hora "21:00" --headless
Bot reserva SmartFit, por https://deivid.xyz
********************************************

Hora disponible: 24/11 08:00
Hora disponible: 24/11 09:00
Hora disponible: 24/11 10:00
Hora disponible: 24/11 11:00
Hora disponible: 24/11 12:00
Hora disponible: 24/11 13:00
Hora disponible: 24/11 14:00
Hora disponible: 24/11 15:00
Hora disponible: 24/11 16:00
Hora disponible: 24/11 17:00
Hora disponible: 24/11 18:00
Hora disponible: 24/11 19:00
Hora disponible: 24/11 21:00
Hora reservada! 2021-11-24 a las 21:00

deivid@deivid-pc:~>
```

## Uso programado

Pueden usar el script de manera automática incluyéndolo en su `crontab` de usuario (Linux/OS X):

```
# script con ruta absoluta

# Explicacion: Ejecuta el script todos los díás a las 10 am, para pedir hora a las 20:00, para dos días más. Solo se reservará la hora si es martes o jueves.
0 10 * * * /home/deivid/PycharmProjects/smartfit/smartfit_bot.py --usuario <tu_rut> --password <tu_password> --hora "20:00" --horizonte 2 --dias_allowed mar jue
```
Puedes incluir varias lineas que invoquen al proceso a diferentes horas/días, para maximizar la probabilidad de alcanzar hora.

Usuarios Windows pueden ingresar una entrada en el Programador de Tareas.

## TODOs

- Guardar registro de horas tomadas en BD SQL(lite).
- Priorizar rangos de hora
- Adaptar para plan Black
