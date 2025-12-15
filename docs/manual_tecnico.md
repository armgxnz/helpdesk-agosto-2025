FRONT-END:
    En el front-end está ubicado todo lo que verá el usuario al acceder a la página. Está diseñado para que dependiendo de qué rol tenga el usuario, se muestre cierta información.
BACK-END:
    Aquí está ubicada toda la lógica detrás de la página. Por aquí se envía toda la información de la base de datos hacia los HTML de la web app.
BASE DE DATOS:
    En esta base de datos se encuentran 3 tablas. La tabla de los usuarios, en donde se almacenan el id, los nombres, emails, contraseñas y roles de los usuarios. Luego, está la tabla de tickets, en la cual está el id, títulos, descripciones, estatus, prioridad, created_at, updated_at, created_by y assigned_to. Y por último, está la tabla de ticket_comments, en el que está ticket_id, user_id, comment, created_at.

MODIFICACIONES:
    Se creó un nuevo endpoint llamado register, en el cual el usuario puede crear una nueva cuenta. Por 'default' se le otorgará el rol de 'USER'.

    Se modificó la forma en la que se accede a un detalle del ticket. En vez de acceder presionando el id, se agregó un botón para que sea más visible para el usuario.

    Los usuarios de ADMIN y AGENT no tienen la opción de crear un ticket.

La base de datos está creada con MariaDB.
Para crearla ejecutarás las siguientes consulta:
    CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    USE helpdesk_db;

    CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'AGENT', 'USER') NOT NULL DEFAULT 'USER',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL, description TEXT NOT NULL,
    status ENUM('OPEN', 'IN_PROGRESS', 'RESOLVED') NOT NULL DEFAULT 'OPEN',
    priority ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL DEFAULT 'MEDIUM',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL,
    assigned_to INT NULL,
    CONSTRAINT fk_tickets_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_tickets_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id)
    );

    CREATE TABLE ticket_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comments_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id)
    );

En el .env se colocará lo siguiente:
    SECRET_KEY= "final_proyect"
    DB_HOST= "localhost"
    DB_USER= "your_user"
    DB_PASSWORD= "your_password"
    DB_NAME= "helpdesk_db"

Para instalar las dependencias colocarás lo siguiente:
    pip install -r requirements.txt

Para correr el código:
    # Windows
        python app.py

    # MacOS/Linux
        python3 app.py

RUTAS PRINCIPALES:
    dashboard:
        En él se encuentra el resumen de los tickets, y también desde ahí, tienes un botón en el que te lleva a crear un ticket o ver la lista de tickets
    register:
        Este endpoint es para la creacion de usuarios
    login:
        Aquí inicias sesión para acceder a tu cuenta
    logout:
        Esta ruta es para cerrar sesión
    tickets_list:
        Desde esta ruta puedes ver la lista de los tickets
    ticket_new:
        Desde este endpoint puedes crear un nuevo ticket, colocando el título, descripción, e importancia del ticket.
    ticket_detail:
        En este endpoint puedes ver los detalles de un ticket
    ticket_update:
        Desde aquí puedes actualizar un ticket
    comment_add:
        Se agrega un comentario a la seccion de ticket_detail
    users_list:
        Te muestra la lista de todos los usuarios registrados en la pagina
    user_change_role:
        Esta acción es exclusica para los admin. Gracias a esto, un admin puede cambiar los roles de un usuario.

URL GITHUB:
    https://github.com/armgxnz/helpdesk-agosto-2025