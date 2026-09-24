# Inventario de equipos TIC

Proyecto de Implantación de Aplicaciones Web (2.º de ASIR). Permite registrar el equipamiento informático de un centro desde un formulario y guardar cada ficha en MySQL.

## Qué hace la aplicación

1. El navegador solicita `GET /` y Flask muestra el formulario de `templates/index.html` con sus estilos de `static/style.css`.
2. Al enviarlo, `POST /equipos` recibe `tipo`, `marca`, `modelo`, `aula` y `estado`.
3. `app.py` comprueba los campos, conecta con MySQL y ejecuta un `INSERT` parametrizado en `inventario.equipos`.
4. Después de `commit()`, `templates/confirmacion.html` muestra el identificador y los datos registrados.

Se ha comprobado en Ubuntu que el formulario inserta equipos en la base de datos y muestra la confirmación. El repositorio no incluye una configuración de Apache; más abajo se explica cómo conectarlo a Flask si se desea acceder a la web a través de Apache.

## Decisiones de proyecto

| Elemento | Decisión | Versión | Justificación |
| --- | --- | --- | --- |
| Sistema operativo | Ubuntu | 24.04 | Entorno Linux real |
| Servidor web | Apache | 2 | Sencillez y popularidad |
| Base de datos | MySQL | Por comprobar en la instalación | Experiencia previa |
| Lenguaje servidor | Python | 3 | Uso muy extendido |
| Framework | Flask | 3 | Sencillez y pensado para uso web |
| Control de versiones | Git | 2 | Uso muy extendido |
| Documentación | Markdown | — | Muy utilizado con GitHub |

El archivo `requirements.txt` fija las versiones concretas de las dependencias Python instaladas en este proyecto. La versión del servidor MySQL se puede consultar con `sudo mysql -e 'SELECT VERSION();'`.

## Archivos del repositorio

```text
inventario_equipos_TIC/
├── .gitignore
├── README.md
├── app.py
├── requirements.txt
├── static/
│   └── style.css
└── templates/
    ├── index.html
    └── confirmacion.html
```

Flask busca las páginas HTML en `templates/` y los estilos en `static/`. La carpeta `venv/` no se sube a GitHub: está excluida en `.gitignore`. Tampoco se sube la contraseña de MySQL.

## Instalación y puesta en marcha, paso a paso

Los siguientes pasos permiten reproducir la práctica en Ubuntu 24.04. Si el proyecto ya está instalado en `/var/www/inventario_equipos_TIC`, no hay que volver a crear la base de datos ni clonar el repositorio.

### 1. Instalar los programas necesarios

```bash
sudo apt update
sudo apt install -y apache2 mysql-server git python3 python3-pip python3-venv
```

Comprobar que Apache y MySQL están activos:

```bash
systemctl is-active apache2
systemctl is-active mysql
```

En ambos casos la salida esperada es `active`.

### 2. Obtener el proyecto y preparar permisos

En una instalación nueva, crear el directorio para la web y clonarla desde GitHub. Sustituir `URL_REAL_DEL_REPOSITORIO` por la dirección real del repositorio; no escribir ese texto literalmente.

```bash
sudo install -d -o "$USER" -g "$(id -gn)" /var/www/inventario_equipos_TIC
git clone URL_REAL_DEL_REPOSITORIO /var/www/inventario_equipos_TIC
cd /var/www/inventario_equipos_TIC
```

El directorio debe pertenecer al usuario de trabajo para poder editar los archivos desde VS Code y utilizar Git sin `sudo`.

### 3. Crear la base de datos, la cuenta y la tabla

Acceder a MySQL como administrador:

```bash
sudo mysql
```

En la consola `mysql>`, ejecutar **solo en una instalación nueva**. Elegir una contraseña propia en vez de `TU_CLAVE` y usar la misma al iniciar la aplicación:

```sql
CREATE DATABASE inventario;

CREATE USER 'inventario'@'localhost' IDENTIFIED BY 'TU_CLAVE';
GRANT ALL PRIVILEGES ON inventario.* TO 'inventario'@'localhost';

USE inventario;

CREATE TABLE equipos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    tipo VARCHAR(30) NOT NULL,
    marca VARCHAR(60) NOT NULL,
    modelo VARCHAR(80) NOT NULL,
    aula VARCHAR(30) NOT NULL,
    estado VARCHAR(30) NOT NULL,
    PRIMARY KEY (id)
);
```

El esquema anterior reproduce la tabla comprobada en la máquina de prácticas. `id` se genera automáticamente y los cinco campos del formulario son obligatorios.

Comprobar estructura y permisos:

```sql
DESCRIBE equipos;
SHOW GRANTS FOR 'inventario'@'localhost';
EXIT;
```

La cuenta `inventario@localhost` tiene permisos sobre `inventario.*`. La contraseña no aparece en los archivos del repositorio.

### 4. Preparar Python, Flask y el conector de MySQL

Dentro del proyecto:

```bash
cd /var/www/inventario_equipos_TIC
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

El entorno virtual evita el error `externally-managed-environment` que aparece al intentar instalar paquetes con `pip` en el Python del sistema. `requirements.txt` incluye Flask y `mysql-connector-python`.

### 5. Ejecutar la aplicación

En la misma terminal donde se activó `venv`, indicar la contraseña del usuario MySQL y arrancar Flask:

```bash
export INVENTARIO_DB_PASSWORD='TU_CLAVE'
python app.py
```

Sustituir `TU_CLAVE` por la contraseña elegida en el paso 3. `app.py` conecta a `localhost` con el usuario `inventario` y la base de datos `inventario`. La variable debe existir en la **misma terminal** desde la que se ejecuta Python.

Abrir en el navegador de esa máquina: **http://127.0.0.1:5000/**. Flask escucha en `127.0.0.1:5000`; mantener abierta la terminal mientras se usa la web. Para pararlo, pulsar `Ctrl+C`; para salir del entorno virtual, ejecutar `deactivate`.

### 6. Registrar un equipo y comprobar la inserción

Rellenar todos los campos y pulsar **Guardar equipo**. Debe aparecer la página de confirmación con el número de ficha. En otra terminal, consultar MySQL:

```bash
sudo mysql -e 'SELECT * FROM inventario.equipos;'
```

En la máquina de prácticas se verificaron, entre otros, estos registros:

| id | tipo | marca | modelo | aula | estado |
| --- | --- | --- | --- | --- | --- |
| 1 | Ordenador | dell | OptiPlex 7010 | taller 2 | Disponible |
| 2 | Monitor | lenovo | thinkpad 330 | taller 3 | En reparación |

Al repetir la instalación desde cero, estos registros no aparecerán hasta introducir equipos mediante el formulario.

### 7. Conectar Apache con Flask, si se va a usar Apache para acceder

**Esta configuración no figura en el ZIP del repositorio y no consta como probada en la máquina de prácticas.** Apache puede recibir las peticiones y enviarlas a Flask, que debe seguir ejecutándose en `127.0.0.1:5000`.

Activar los módulos necesarios:

```bash
sudo a2enmod proxy proxy_http
```

Crear `/etc/apache2/sites-available/inventario_tic.conf`:

```bash
sudo nano /etc/apache2/sites-available/inventario_tic.conf
```

Contenido del archivo:

```apache
<VirtualHost *:80>
    ServerName inventario.test
    ProxyPreserveHost On

    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
</VirtualHost>
```

Activar el sitio y comprobar la configuración:

```bash
sudo a2ensite inventario_tic.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

`configtest` debe mostrar `Syntax OK`. En el Ubuntu desde el que se abre el navegador, añadir a `/etc/hosts`:

```text
127.0.0.1 inventario.test
```

Se puede editar con `sudo nano /etc/hosts`. Con `python app.py` aún en marcha, abrir **http://inventario.test/**. Esa dirección local corresponde al propio Ubuntu; si Flask se detiene, Apache no podrá mostrar la aplicación.

## Git y GitHub

El proyecto ya tiene un repositorio local y se ha publicado en GitHub. Al trabajar desde un clon, comprobar el remoto y guardar las modificaciones del README así:

```bash
cd /var/www/inventario_equipos_TIC
git remote -v
git add README.md
git commit -m "Documentar el proyecto de inventario TIC"
git push
```

En el primer envío desde una rama `main` local todavía sin seguimiento remoto, usar `git push -u origin main`. El archivo `.gitignore` evita incluir `venv/`, archivos `__pycache__/`, `*.pyc` y `.env`.

## Errores que aparecieron durante la práctica

| Problema | Causa y solución aplicada |
| --- | --- |
| `pip install flask` devolvió `externally-managed-environment`. | Ubuntu protege el Python del sistema. Se creó `venv` y se instalaron allí las dependencias. |
| VS Code no podía guardar archivos en `/var/www/inventario_equipos_TIC`. | El directorio pertenecía a `root`. Se corrigió la propiedad con `sudo chown -R "$USER":"$(id -gn)" /var/www/inventario_equipos_TIC`. |
| Git mostró `dubious ownership` y `not in a git directory`. | El directorio del proyecto pertenecía a `root` aunque `.git/` ya pertenecía al usuario. Se corrigió la propiedad del directorio completo. |
| `git push` indicó que `main` no tenía `upstream`. | El primer envío se hizo con `git push -u origin main`. |
| MySQL rechazó el acceso a `inventario_`. | En `app.py` se había escrito `database="inventario_"`, pero la base de datos real es `inventario`. Se corrigió el nombre. |
| Tras insertar un equipo apareció `TemplateNotFound: confirmacion.html`. | La inserción ya se había confirmado con `commit()`; faltaba la plantilla de respuesta. Se añadió `templates/confirmacion.html` y se comprobó la siguiente prueba. |

## Estado actual

La versión incluida en el ZIP **registra** equipos y muestra la ficha recién creada. La consulta de todos los registros se ha realizado desde MySQL; no hay una página de listado, edición o eliminación en la web. La conexión de Apache con Flask se documenta como paso de configuración porque el repositorio no incluye un VirtualHost ni una prueba de esa conexión.