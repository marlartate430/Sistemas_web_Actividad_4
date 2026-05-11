# -*- coding: UTF-8 -*-
import getpass
import sys
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote


from bs4 import BeautifulSoup
import time
import re
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

        if respuesta.status_code == 200:
            self._login = 1
            self._cookie = cookie_valor
            print("Login successful!")
            self._root.destroy()
        else:
            self._login = 0
            messagebox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        metodo = 'GET'
        cabeceras = {'Host': "egela.ehu.eus",
                     'User-Agent': 'Mozilla/5.0 (compatible; Python requests)',
                     'Cookie': 'MoodleSessionegela=' + self._cookie}
        
        # Intentamos obtener la página raíz, que a veces tiene el listado clásico de cursos
        uri_home = "https://egela.ehu.eus/"
        respuesta = requests.request(metodo, uri_home, headers=cabeceras, allow_redirects=True)
        soup_home = BeautifulSoup(respuesta.content, 'html.parser')
        
        print(f"\n##### Debug: Conectado a {respuesta.url}")
        print(f"##### Título de la página: {soup_home.title.string if soup_home.title else 'Sin título'}")
        
        print("\n##### Buscando la asignatura 'Sistemas'... #####")
        all_links = soup_home.find_all('a')
        
        # Mostrar una muestra más amplia de enlaces si no encontramos nada
        if len(all_links) > 0:
            print(f"  Total de enlaces encontrados: {len(all_links)}")
            print("  Muestra de enlaces (primeros 30):")
            for a in all_links[:30]:
                text = a.text.strip()[:30]
                href = a.get('href', '')[:50]
                print(f"    - [{text}] -> {href}")

        course_links = soup_home.find_all('a', href=re.compile(r'course/view\.php\?id='))
        print(f"  Enlaces de tipo curso encontrados: {len(course_links)}")
        for a in course_links:
            text = a.text.strip()
            print(f"    - Curso detectado: '{text}' -> {a['href']}")
            if "SISTEMAS" in text.upper():
                self._curso = a['href']
                print(f"  ¡Asignatura encontrada!: {self._curso}")
                break
        
        # Si no se encuentra con el patrón anterior, probamos con todos los enlaces
        if not self._curso:
            print("  Probando búsqueda general en todos los enlaces...")
            for a in all_links:
                text = a.text.strip()
                if "SISTEMAS" in text.upper():
                    self._curso = a['href']
                    print(f"  ¡Asignatura encontrada (búsqueda general)!: {text} -> {self._curso}")
                    break
        
        if not self._curso:
            print("  [ERROR] No se pudo encontrar ningún enlace que contenga 'Sistemas'.")
            # Dump de los primeros 50 enlaces para diagnóstico
            print("  Listado de los primeros 50 enlaces para diagnóstico:")
            for a in all_links[:50]:
                print(f"    - [{a.text.strip()[:30]}] -> {a.get('href', '')[:50]}")
            popup.destroy()
            return self._refs

        # Ahora vamos a la página de la asignatura
        respuesta = requests.request(metodo, self._curso, headers=cabeceras, allow_redirects=True)
        soup_asignatura = BeautifulSoup(respuesta.content, 'html.parser')
        
        # Buscar todas las secciones/pestañas
        pestañas = soup_asignatura.find_all('a', class_='nav-link')
        urls_temas = [a['href'] for a in pestañas if '&section=' in a.get('href', '')]
        if not urls_temas:
            urls_temas = [self._curso]
        
        urls_temas = list(set(urls_temas))
        
        for url_tema in urls_temas:
            res_tema = requests.get(url_tema, headers=cabeceras, allow_redirects=True)
            soup_tema = BeautifulSoup(res_tema.content, 'html.parser')
            recursos = soup_tema.find_all('div', class_='activity-instance')
            
            for recurso in recursos:
                enlace = recurso.find('a')
                if not enlace or not enlace.has_attr('href'):
                    continue
                
                # Comprobar si es PDF
                es_pdf = "pdf" in enlace.text.lower() or recurso.find('img', src=re.compile(r'pdf'))
                if es_pdf:
                    url_recurso = enlace['href']
                    
                    # Limpiar nombre
                    span_nombre = enlace.find('span', class_='instancename')
                    if span_nombre:
                        oculto = span_nombre.find('span', class_='accesshide')
                        if oculto:
                            oculto.decompose()
                        nombre_pdf = span_nombre.text.strip()
                    else:
                        nombre_pdf = enlace.text.strip()
                    
                    if not nombre_pdf.lower().endswith(".pdf"):
                        nombre_pdf += ".pdf"
                    
                    self._refs.append({'pdf_name': nombre_pdf, 'pdf_link': url_recurso})
                    
                    # Actualizar barra de progreso
                    progress += 5
                    if progress > 100: progress = 100
                    progress_var.set(progress)
                    progress_bar.update()

        popup.destroy()
        return self._refs

    def get_pdf(self, selection):
        print("\t##### descargando  PDF... #####")
        pdf_name = self._refs[selection]['pdf_name']
        pdf_link = self._refs[selection]['pdf_link']
        
        cabeceras = {'Host': "egela.ehu.eus",
                     'User-Agent': 'Mozilla/5.0 (compatible; Python requests)',
                     'Cookie': 'MoodleSessionegela=' + self._cookie}
        
        # Añadir redirect=1 para forzar descarga
        url_descarga = f"{pdf_link}&redirect=1" if '?' in pdf_link else pdf_link
        respuesta = requests.get(url_descarga, headers=cabeceras, allow_redirects=True)
        
        # Manejar redirección pluginfile.php si es necesario
        if 'text/html' in respuesta.headers.get('Content-Type', ''):
            soup = BeautifulSoup(respuesta.content, 'html.parser')
            link_real = soup.find('a', href=re.compile(r'pluginfile\.php'))
            if link_real:
                respuesta = requests.get(link_real['href'], headers=cabeceras, allow_redirects=True)
        
        pdf_content = respuesta.content
        return pdf_name, pdf_content