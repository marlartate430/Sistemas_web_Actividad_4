import requests
import urllib.parse
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import os
from dotenv import load_dotenv
import helper

load_dotenv()

app_key = os.getenv('DROPBOX_APP_KEY')
app_secret = os.getenv('DROPBOX_APP_SECRET')
server_addr = "localhost"
server_port = 8070
redirect_uri = "http://" + server_addr + ":" + str(server_port)


class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None
    _msg_listbox = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        # por el puerto 8070 esta escuchando el servidor que generamos
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((server_addr, server_port))
        server_socket.listen(1)
        print("\tLocal server listening on port " + str(server_port))

        # recibe la redireccio 302 del navegador
        client_connection, client_address = server_socket.accept()
        peticion = client_connection.recv(1024)
        print("\tRequest from the browser received at local server:")
        print(peticion)

        # buscar en solicitud el "auth_code"
        primera_linea = peticion.decode('UTF8').split('\n')[0]
        aux_auth_code = primera_linea.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print("\tauth_code: " + auth_code)

        # devolver una respuesta al usuario
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"
        client_connection.sendall(http_response.encode('utf-8'))
        client_connection.close()
        server_socket.close()

        return auth_code

    def do_oauth(self):
        print("/do_oauth")
        # PARTE 1: Abrir en el navegador la URI https://www.dropbox.com/oauth2/authorize
        params = {
            'response_type': 'code',
            'client_id': app_key,
            'redirect_uri': redirect_uri
        }
        url = "https://www.dropbox.com/oauth2/authorize?" + urllib.parse.urlencode(params)
        webbrowser.open_new(url)

        # PARTE 2: Recibir el auth_code con el servidor local
        auth_code = self.local_server()

        # PARTE 3: Obtener el TOKEN https://api.dropboxapi.com/oauth2/token
        token_url = "https://api.dropboxapi.com/oauth2/token"
        data = {
            'code': auth_code,
            'grant_type': 'authorization_code',
            'client_id': app_key,
            'client_secret': app_secret,
            'redirect_uri': redirect_uri
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(token_url, data=data, headers=headers)

        if response.status_code == 200:
            json_resp = response.json()
            self._access_token = json_resp['access_token']
            print("\tAccess_Token: " + self._access_token)
            self._root.destroy()
        else:
            print("\tError obtaining access token: " + response.text)

    def _sanitize_path(self, path):
        if not path or path == "/":
            return ""
        # Ensure path starts with / and has no trailing /
        path = path.strip()
        if not path.startswith("/"):
            path = "/" + path
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]
        return path

    def list_folder(self, msg_listbox):
        print("/list_folder")
        uri = 'https://api.dropboxapi.com/2/files/list_folder'

        path = self._sanitize_path(self._path)
        print(f"\tListing path: '{path}'")

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/json'
        }
        data = {
            "path": path,
            "recursive": False,
            "include_media_info": False,
            "include_deleted": False,
            "include_has_explicit_shared_members": False,
            "include_mounted_folders": True,
            "include_non_downloadable_files": True
        }

        response = requests.post(uri, headers=headers, json=data)

        if response.status_code == 200:
            contenido_json = response.json()
            self._files = helper.update_listbox2(msg_listbox, self._path, contenido_json)
        else:
            print(f"\tError listing folder ({response.status_code}): {response.text}")

    def transfer_file(self, file_path, file_data):
        print("/upload")
        uri = 'https://content.dropboxapi.com/2/files/upload'

        file_path = self._sanitize_path(file_path)
        print(f"\tUploading to: '{file_path}'")

        argumentos_api = {
            "path": file_path,
            "mode": "overwrite",
            "autorename": False,
            "mute": False,
            "strict_conflict": False
        }

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Dropbox-API-Arg': json.dumps(argumentos_api),
            'Content-Type': 'application/octet-stream'
        }

        response = requests.post(uri, headers=headers, data=file_data)

        if response.status_code == 200:
            print(f"\tFile {file_path} uploaded successfully")
        else:
            print(f"\tError uploading file ({response.status_code}): {response.text}")

    def delete_file(self, file_path):
        print("/delete_file")
        uri = 'https://api.dropboxapi.com/2/files/delete_v2'

        file_path = self._sanitize_path(file_path)
        print(f"\tDeleting: '{file_path}'")

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/json'
        }
        data = {
            "path": file_path
        }

        response = requests.post(uri, headers=headers, json=data)

        if response.status_code == 200:
            print(f"\tFile/Folder {file_path} deleted successfully")
        else:
            print(f"\tError deleting file/folder ({response.status_code}): {response.text}")

    def download_file(self, file_path, destino_local):
        print("/download_file")
        uri = 'https://content.dropboxapi.com/2/files/download'

        file_path = self._sanitize_path(file_path)
        print(f"\tDownloading: '{file_path}' -> '{destino_local}'")

        argumentos_api = {"path": file_path}

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Dropbox-API-Arg': json.dumps(argumentos_api),
        }

        response = requests.post(uri, headers=headers)

        if response.status_code == 200:
            with open(destino_local, 'wb') as f:
                f.write(response.content)
            print(f"\tFile saved to '{destino_local}'")
            return True
        else:
            print(f"\tError downloading file ({response.status_code}): {response.text}")
            return False

    def share_file(self, file_path):
        print("/share_file")
        uri = 'https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings'

        file_path = self._sanitize_path(file_path)
        print(f"\tCreating shared link for: '{file_path}'")

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/json'
        }
        data = {
            "path": file_path,
            "settings": {
                "requested_visibility": "public"
            }
        }

        response = requests.post(uri, headers=headers, json=data)

        if response.status_code == 200:
            url = response.json().get('url', '')
            print(f"\tShared link: {url}")
            return url
        elif response.status_code == 409:
            # El link ya existe, lo conseguimos de nuevo
            error_data = response.json()
            existing_url = (error_data
                            .get('error', {})
                            .get('shared_link_already_exists', {})
                            .get('metadata', {})
                            .get('url', ''))
            if existing_url:
                print(f"\tExisting shared link: {existing_url}")
                return existing_url
            # Si no viene en el error, llamamos a list_shared_links
            uri_list = 'https://api.dropboxapi.com/2/sharing/list_shared_links'
            resp2 = requests.post(uri_list, headers=headers, json={"path": file_path, "direct_only": True})
            if resp2.status_code == 200:
                links = resp2.json().get('links', [])
                if links:
                    url = links[0].get('url', '')
                    print(f"\tRecovered existing shared link: {url}")
                    return url
            print(f"\tCould not retrieve existing link: {response.text}")
            return None
        else:
            print(f"\tError creating shared link ({response.status_code}): {response.text}")
            return None

    def create_folder(self, path):
        print("/create_folder")
        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'

        path = self._sanitize_path(path)
        print(f"\tCreating folder: '{path}'")

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/json'
        }
        data = {
            "path": path,
            "autorename": False
        }

        response = requests.post(uri, headers=headers, json=data)

        if response.status_code == 200:
            print(f"\tFolder {path} created successfully")
        else:
            print(f"\tError creating folder ({response.status_code}): {response.text}")