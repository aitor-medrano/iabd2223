#!/usr/bin/python3

import sys

# inicializamos el diccionario
dictPalabras = {}

for linea in sys.stdin:
    # quitamos espacios de sobra
    linea = linea.strip()
    # parseamos la entrada de mapper.py
    palabra, cuenta = linea.split('\t', 1)
    # la pasamos a minúscula
    palabra = palabra.lower()
    # convertimos cuenta de string a int
    try:
        cuenta = int(cuenta)
    except ValueError:
        # cuenta no era un numero, descartamos la linea
        continue

    try:
        dictPalabras[palabra] += cuenta
    except:
        dictPalabras[palabra] = cuenta

for palabra in dictPalabras.keys():
    print(palabra, "\t", dictPalabras[palabra])
