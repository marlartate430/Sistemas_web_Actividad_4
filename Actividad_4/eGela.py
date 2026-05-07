# -*- coding: UTF-8 -*-
import getpass
import sys
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote

import self
from bs4 import BeautifulSoup
import time
import helper


class eGela:
    _login = 0
    _cookie = ""
    _curso = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root


    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. PETICION #####")
        metodo = 'GET'
        uri1 = "https://egela.ehu.eus/login/index.php"
        cabeceras = {'Host': "egela.ehu.eus",
                     'User-Agent': 'Mozilla/5.0 (compatible; Python requests)', }
        cuerpo = ''

        print('\nSOLICITUD:')
        print('Metodo:' + metodo)
        print('Uri:' + uri1 + '\n')

        respuesta = requests.request(metodo, uri1, headers=cabeceras, data=cuerpo, allow_redirects=False)

        print('RESPUESTA:')
        codigo = respuesta.status_code
        descripcion = respuesta.reason
        print(str(codigo) + ': ' + descripcion)
        print('Cookie:' + str(respuesta.headers.get('Set-cookie')) + '\n')

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)


        print("\n##### 2. PETICION #####")
        if respuesta.status_code == 200:
            documento = BeautifulSoup(respuesta.content, 'html.parser')

            logintoken = documento.find('input', {'name': 'logintoken'})['value']


            metodo = 'POST'
            cuerpo = 'logintoken=' + logintoken + '&username=' + str(username) + '&password=' + str(password)
            cookie_valor = respuesta.cookies.get('MoodleSessionegela')
            cabeceras = {'Host': "egela.ehu.eus",
                         'Content-Type': "application/x-www-form-urlencoded",
                         'Content-Length': str(len(cuerpo)),
                         'Cookie': 'MoodleSessionegela=' + cookie_valor}

            print('\n -----------------------------------------------\n')
            print('SOLICITUD:')
            print('Metodo:' + metodo)
            print('Uri:' + uri1)
            print('Cuerpo:' + cuerpo + '\n')

            respuesta = requests.request(metodo, uri1, headers=cabeceras, data=cuerpo, allow_redirects=False)

            print('RESPUESTA:')
            codigo = respuesta.status_code
            descripcion = respuesta.reason
            print(str(codigo) + ': ' + descripcion)
            print('Cookie:' + str(respuesta.headers.get('Set-cookie')))
            print('Location:' + str(respuesta.headers.get('Location')))

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 3. PETICION #####")

        if respuesta.status_code == 303:
            metodo = 'GET'
            uri2 = respuesta.headers['location']
            cookie_valor = respuesta.cookies.get('MoodleSessionegela')
            cabeceras = {'Host': "egela.ehu.eus",
                         'User-Agent': 'Mozilla/5.0 (compatible; Python requests)',
                         'Cookie': 'MoodleSessionegela=' + str(cookie_valor)}
            cuerpo = ''

            print('\n -----------------------------------------------\n')
            print('SOLICITUD:')
            print('Metodo:' + metodo)
            print('Uri:' + uri2 + '\n')

            respuesta = requests.request(metodo, uri2, headers=cabeceras, data=cuerpo, allow_redirects=False)

            print('RESPUESTA:')
            codigo = respuesta.status_code
            descripcion = respuesta.reason
            print(str(codigo) + ': ' + descripcion)
            print('Location:' + str(respuesta.headers.get('Location')))

            progress = 75
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(1)
            popup.destroy()

        print("\n##### 4. PETICION #####")

        if respuesta.status_code == 303:
            metodo = 'GET'
            uri3 = respuesta.headers['location']
            cabeceras = {'Host': "egela.ehu.eus",
                         'User-Agent': 'Mozilla/5.0 (compatible; Python requests)',
                         'Cookie': 'MoodleSessionegela=' + cookie_valor}
            cuerpo = ''

            print('\n -----------------------------------------------\n')
            print('SOLICITUD:')
            print('Metodo:' + metodo)
            print('Uri:' + uri3 + '\n')

            respuesta = requests.request(metodo, uri3, headers=cabeceras, data=cuerpo, allow_redirects=False)

            print('RESPUESTA:')
            codigo = respuesta.status_code
            descripcion = respuesta.reason
            print(str(codigo) + ': ' + descripcion)

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()

        if COMPROBACION_DE_LOG_IN:
            #############################################
            # ACTUALIZAR VARIABLES
            #############################################
            self._root.destroy()
        else:
            messagebox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. PETICION (Página principal de la asignatura en eGela) #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress_step = float(100.0 / len(NUMERO_DE_PDF_EN_EGELA))


        print("\n##### Analisis del HTML... #####")
        #############################################
        # ANALISIS DE LA PAGINA DEL AULA EN EGELA
        # PARA BUSCAR PDFs
        #############################################

        # INICIALIZA Y ACTUALIZAR BARRA DE PROGRESO
        # POR CADA PDF ANIADIDO EN self._refs

        progress_step = float(100.0 / len(NUMERO_DE_PDF_EN_EGELA))


                progress += progress_step
                progress_var.set(progress)
                progress_bar.update()
                time.sleep(0.1)

        popup.destroy()
        return self._refs

    def get_pdf(self, selection):

        print("\t##### descargando  PDF... #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        return pdf_name, pdf_content