# 🎬 Proyecto: Gestión de Películas con Docker

Aplicación web con balanceo de carga, dos nodos Flask y replicación bidireccional de base de datos MySQL.

---

## 📁 Estructura del proyecto

```
proyecto/
├── docker-compose.yml       # Define todos los contenedores
├── Dockerfile               # Construye la imagen de Flask
├── app2.py                  # Código Python con Flask
├── nginx/
│   └── nginx.conf           # Configuración del balanceador
└── templates/
    └── index.html           # Interfaz web
```

---

## 🐳 Contenedores que se crean

| Contenedor | Qué hace | Puerto |
|---|---|---|
| `Maestro` | Base de datos principal | 3306 |
| `Esclavo` | Base de datos secundaria | 3307 |
| `nodo1` | App Flask → conectada al Maestro | — |
| `nodo2` | App Flask → conectada al Esclavo | — |
| `nginx_balancer` | Balanceador de carga | 80 |
| `phpmyadmin` | Gestor visual de bases de datos | 8080 |

---

## 🚀 Cómo levantar el proyecto

```powershell
docker-compose up -d --build
```

Para limpiar todo y empezar desde cero:
```powershell
docker-compose down -v
docker-compose up -d --build
```

---

## 🌐 URLs de acceso

| URL | Qué abre |
|---|---|
| http://localhost | Aplicación web |
| http://localhost:8080 | phpMyAdmin |

---

## 🗄️ Configurar la base de datos

Después de levantar los contenedores, entra a phpMyAdmin (`http://localhost:8080`) conectado al **Maestro** y crea la tabla:

```sql
USE cine;

CREATE TABLE peliculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    director VARCHAR(100),
    anio INT,
    genero VARCHAR(50)
);
```

---

## 🔄 Configurar la replicación bidireccional

### PASO 1 — Crear usuario replicador en el Maestro

```powershell
docker exec -it Maestro mysql -uroot -proot
```

```sql
DROP USER IF EXISTS 'replicador'@'%';
CREATE USER 'replicador'@'%' IDENTIFIED WITH mysql_native_password BY 'replica123';
GRANT REPLICATION SLAVE ON *.* TO 'replicador'@'%';
FLUSH PRIVILEGES;
SHOW MASTER STATUS;
```
Anota el `File` y `Position`.

### PASO 2 — Crear usuario replicador en el Esclavo

```powershell
docker exec -it Esclavo mysql -uroot -proot
```

```sql
DROP USER IF EXISTS 'replicador'@'%';
CREATE USER 'replicador'@'%' IDENTIFIED WITH mysql_native_password BY 'replica123';
GRANT REPLICATION SLAVE ON *.* TO 'replicador'@'%';
FLUSH PRIVILEGES;
FLUSH LOGS;
SHOW MASTER STATUS;
```
Anota el `File` y `Position`.

### PASO 3 — En phpMyAdmin → Esclavo

Usa los valores del PASO 1:
```sql
STOP SLAVE;
RESET SLAVE ALL;
CHANGE MASTER TO
  MASTER_HOST='mysql_master',
  MASTER_USER='replicador',
  MASTER_PASSWORD='replica123',
  MASTER_LOG_FILE='aqui_file_maestro',
  MASTER_LOG_POS=aqui_position_maestro;
START SLAVE;
SHOW SLAVE STATUS;
```
Verifica: `Slave_IO_Running: Yes` y `Slave_SQL_Running: Yes`

### PASO 4 — En phpMyAdmin → Maestro

Usa los valores del PASO 2:
```sql
STOP SLAVE;
RESET SLAVE ALL;
CHANGE MASTER TO
  MASTER_HOST='mysql_slave',
  MASTER_USER='replicador',
  MASTER_PASSWORD='replica123',
  MASTER_LOG_FILE='aqui_file_esclavo',
  MASTER_LOG_POS=aqui_position_esclavo;
START SLAVE;
SHOW SLAVE STATUS;
```
Verifica: `Slave_IO_Running: Yes` y `Slave_SQL_Running: Yes`

---

## ✏️ Cómo modificar el HTML

1. Edita `templates/index.html`
2. Reconstruye solo los nodos:
```powershell
docker-compose up -d --build nodo1 nodo2
```

---

## ⚠️ Orden correcto siempre

1. `docker-compose down -v` — limpiar
2. `docker-compose up -d --build` — levantar
3. Configurar replicación
4. Crear tabla desde el Maestro
5. Insertar datos

---

## 📸 Capturas de pantalla

### 1. Contenedores corriendo
Ejecuta `docker ps` y toma captura mostrando los 6 contenedores activos:
`Maestro`, `Esclavo`, `nodo1`, `nodo2`, `nginx_balancer`, `phpmyadmin`

### 2. Base de datos Maestro
En phpMyAdmin conectado al Maestro (`mysql_master`):
- Captura de la tabla `peliculas` con los registros insertados
- Captura del resultado de `SHOW SLAVE STATUS` mostrando `Slave_IO_Running: Yes` y `Slave_SQL_Running: Yes`

### 3. Base de datos Esclavo
En phpMyAdmin conectado al Esclavo (`mysql_slave`):
- Captura de la tabla `peliculas` con los mismos registros replicados
- Captura del resultado de `SHOW SLAVE STATUS` mostrando `Slave_IO_Running: Yes` y `Slave_SQL_Running: Yes`

### 4. Aplicación web — Nodo 1
Abre `http://localhost` y toma captura mostrando:
- El badge superior indicando **Nodo 1** y **mysql_master**
- La tabla con los registros cargados

### 5. Aplicación web — Nodo 2
Recarga la página y toma captura mostrando:
- El badge superior indicando **Nodo 2** y **mysql_slave**
- La tabla con los mismos registros

### 6. Insertar un registro
- Captura del formulario con los campos llenos
- Captura del mensaje de confirmación `✅ Guardado en Nodo X`

### 7. Verificar replicación bidireccional
- Inserta un registro desde el Maestro en phpMyAdmin y toma captura del mismo registro apareciendo en el Esclavo
- Repite al revés: inserta desde el Esclavo y muestra que aparece en el Maestro
