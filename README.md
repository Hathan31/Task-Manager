# Task Manager Application

## Descripción del Proyecto
El **Task Manager** es una aplicación desarrollada en Python con interfaz gráfica basada en Tkinter. Está diseñada para ayudar a los usuarios a organizar sus tareas de manera eficiente, permitiendo gestionar tareas por días, semanas o meses, además de categorizar por prioridad, estado y más.

---

## Características

- **Inicio de sesión y registro de usuarios**:
  - Permite registrar nuevos usuarios y gestionar sesiones.
- **Gestor de tareas**:
  - Agregar, editar y eliminar tareas.
  - Visualización de tareas por día, semana y mes.
  - Filtros por título, fecha, prioridad y estado.
  - Estadísticas visuales mediante gráficos de pastel.
- **Interfaz intuitiva**:
  - Diseñada con Tkinter y organizada con pestañas.
  - Barras de búsqueda y opciones de ordenación de tareas.
- **Base de datos MySQL**:
  - Persistencia de datos en tablas `users` y `tasks`.

---

## Requisitos del Sistema

1. **Python 3.7 o superior**
2. **Librerías necesarias**:
   - `mysql-connector-python`
   - `tkinter` (incluido por defecto en Python)
   - `matplotlib`
3. **Servidor MySQL**

---

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/task-manager.git
   ```

2. Navega al directorio del proyecto:
   ```bash
   cd task-manager
   ```

3. Instala las dependencias requeridas:
   ```bash
   pip install mysql-connector-python matplotlib
   ```

4. Configura la base de datos:
   - Inicia tu servidor MySQL.
   - Ejecuta el script `tasks.sql` para crear las tablas necesarias:
     ```sql
     CREATE DATABASE taskManager;
     USE taskManager;

     CREATE TABLE users (
         id INT AUTO_INCREMENT PRIMARY KEY,
         username VARCHAR(255) UNIQUE
     );

     CREATE TABLE tasks (
         id INT AUTO_INCREMENT PRIMARY KEY,
         user_id INT NOT NULL,
         title VARCHAR(255),
         due_date DATE,
         priority ENUM('Normal', 'Medium', 'High'),
         comments TEXT,
         status ENUM('Pending', 'In Progress', 'Completed'),
         FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
     );
     ```

5. Actualiza la configuración de la base de datos en `database.py`:
   ```python
   db_connection = mysql.connector.connect(
       host="localhost",
       user="tu_usuario",
       password="tu_contraseña",
       database="taskManager"
   )
   ```

---

## Uso

1. Ejecuta el archivo principal:
   ```bash
   python app.py
   ```

2. **Registro e inicio de sesión**:
   - Registra un nuevo usuario o ingresa un nombre de usuario existente.

3. **Gestor de tareas**:
   - Usa las opciones de la interfaz para agregar, editar o eliminar tareas.
   - Navega entre las pestañas de día, semana y mes para ver las tareas correspondientes.
   - Aplica filtros o reordena tareas según tus necesidades.

4. **Gráficos de progreso**:
   - Haz clic en "Task Completion" para visualizar un gráfico de pastel con el estado de tus tareas.

---

## Archivos del Proyecto

1. **`app.py`**:
   - Punto de entrada principal que gestiona el inicio de sesión y registro de usuarios.

2. **`database.py`**:
   - Gestiona la conexión con la base de datos MySQL.

3. **`taskManager.py`**:
   - Implementa la lógica principal para gestionar tareas y la interfaz gráfica.

4. **`tasks.sql`**:
   - Script para crear y configurar las tablas de la base de datos.

---

## Autor
**Jonathan Sampera**


