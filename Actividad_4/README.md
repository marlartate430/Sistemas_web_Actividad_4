# eGela2Dropbox

---

## Requisitos previos
### Archivo `.env`

El código lee las credenciales de tu app de Dropbox desde un archivo llamado `.env` en la misma carpeta que los scripts. Créalo así:

```
DROPBOX_APP_KEY=tu_app_key_aqui
DROPBOX_APP_SECRET=tu_app_secret_aqui
```

### Permisos necesarios (Scopes)
  
| Permiso | Para qué se usa |
|---|---|
| `files.content.read` | Descargar archivos y listar carpetas |
| `files.content.write` | Subir y eliminar archivos |
| `files.metadata.read` | Leer metadatos de archivos y carpetas |
| `sharing.write` | Generar enlaces compartidos públicos |

---

## Cómo ejecutar
```bash
python actividad_4.py
```

---

## Cómo usar la aplicación

Primero tendrás que poner tu usuario y contraseña de Egela en la primera ventana y en la segunda tendrás que darle a "Login" y darle permiso a DropBox desde el navegador.

### Ventana 3 — Panel principal

Es la ventana principal de trabajo. Tiene dos paneles:

| Panel izquierdo | Panel derecho |
|---|---|
| Lista de PDFs disponibles en eGela | Contenido del directorio actual de Dropbox |

**Acciones disponibles:**

- **`>>>`** — Pasa el PDF seleccionado del panel izquierdo al directorio del panel derecho (Puedes seleccionar varios con `Ctrl+clic`).
- **Delete** — Elimina los archivos o carpetas seleccionados en Dropbox.
- **Create folder** — Crea una nueva carpeta dentro del directorio actual de Dropbox.
- **Download** — Descarga los archivos seleccionados de Dropbox a la carpeta `Downloads` de tu equipo.
- **Share** — Genera un enlace público para el archivo seleccionado (si se selecciona más de un archivo, solo hace el de más arriba).

