# 42campus_ft_transcendence

Este es un proyecto llamado "Transcendence" desarrollado en la escuela 42. El objetivo principal es crear una aplicación web para gestionar torneos de ping pong entre jugadores.

## Funcionalidades

- Registro y autenticación de usuarios.
- Creación y gestión de torneos.
- Clasificación de jugadores según sus resultados en los torneos.

## Configuración del .env.dev

DEBUG=0
SECRET_KEY=mi_secreto_super_seguro
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=database_sql
SQL_USER=usuario_sql
SQL_PASSWORD=password_sql
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres
ADMINPASS=adminpass
STAFFPASS=staffpass
ID="..."
SECRET="..."
COADDR="0xb..."
PRKEY="7c5..."
TZ=Europe/Madrid


## Instrucciones de Uso

1. Clona este repositorio en tu máquina local.
2. Instala las dependencias ejecutando `docker-compose up -d --build`.
5. Accede a la aplicación en tu navegador en `https://localhost`.

## Ejemplos de Uso

- Crea un torneo desde la interfaz de administración.
- Registra a los jugadores y asigna partidos.
- Consulta la clasificación actualizada en tiempo real.

## Autores

- @salaesteve2
- @mikevgb
- @valarcon42madrid
