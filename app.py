from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    return pymysql.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        db=app.config['DB_NAME'],
        cursorclass=pymysql.cursors.DictCursor,
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_role" not in session or session["user_role"] not in roles: 
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    # If user is logged in, redirect to dashboard
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session["user_id"]
    user_role = session["user_role"]

    conn = get_db_connection()
    with conn.cursor() as cursor:
        # ADMIN y AGENT pueden ver todo
        if user_role in ["ADMIN", "AGENT"]:
            # Estadísticas generales
            cursor.execute("SELECT COUNT(*) AS total FROM tickets")
            total_tickets = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE status='OPEN'")
            open_tickets = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE status='IN_PROGRESS'")
            in_progress_tickets = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE status='RESOLVED'")
            resolved_tickets = cursor.fetchone()["total"]

            # Tickets por prioridad
            cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE priority='HIGH' AND status != 'RESOLVED'")
            high_priority = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE priority='MEDIUM' AND status != 'RESOLVED'")
            medium_priority = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE priority='LOW' AND status != 'RESOLVED'")
            low_priority = cursor.fetchone()["total"]

            # Tickets sin asignar
            cursor.execute("SELECT COUNT(*) AS total FROM tickets WHERE assigned_to IS NULL AND status != 'RESOLVED'")
            unassigned_tickets = cursor.fetchone()["total"]

            # Tickets urgentes (HIGH priority + OPEN)
            cursor.execute("""
                SELECT t.id, t.title, t.created_at, u.name AS created_by_name
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                WHERE t.priority = 'HIGH' AND t.status IN ('OPEN', 'IN_PROGRESS')
                ORDER BY t.created_at DESC
                LIMIT 5
            """)
            urgent_tickets = cursor.fetchall()

            # Actividad reciente
            cursor.execute("""
                SELECT t.id, t.title, t.status, t.priority, t.created_at, 
                       u.name AS created_by_name, a.name AS assigned_to_name
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                LEFT JOIN users a ON t.assigned_to = a.id
                ORDER BY t.created_at DESC
                LIMIT 10
            """)
            recent_tickets = cursor.fetchall()

            # Para AGENT: mis tickets asignados
            if user_role == "AGENT":
                cursor.execute("""
                    SELECT COUNT(*) AS total 
                    FROM tickets 
                    WHERE assigned_to=%s AND status != 'RESOLVED'
                """, (user_id,))
                my_assigned = cursor.fetchone()["total"]
            else:
                my_assigned = None

            stats = {
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "in_progress_tickets": in_progress_tickets,
                "resolved_tickets": resolved_tickets,
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority,
                "unassigned_tickets": unassigned_tickets,
                "my_assigned": my_assigned,
                "urgent_tickets": urgent_tickets,
                "recent_tickets": recent_tickets
            }

        # USER solo ve sus propios tickets
        else:
            cursor.execute("""
                SELECT COUNT(*) AS total 
                FROM tickets WHERE created_by=%s
            """, (user_id,))
            total_user_tickets = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total 
                FROM tickets 
                WHERE created_by=%s AND status='OPEN'
            """, (user_id,))
            user_open = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total 
                FROM tickets 
                WHERE created_by=%s AND status='IN_PROGRESS'
            """, (user_id,))
            user_in_progress = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total 
                FROM tickets 
                WHERE created_by=%s AND status='RESOLVED'
            """, (user_id,))
            user_resolved = cursor.fetchone()["total"]

            # Tickets del usuario por prioridad (no resueltos)
            cursor.execute("""
                SELECT COUNT(*) AS total 
                FROM tickets 
                WHERE created_by=%s AND priority='HIGH' AND status != 'RESOLVED'
            """, (user_id,))
            user_high = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total 
                FROM tickets 
                WHERE created_by=%s AND priority='MEDIUM' AND status != 'RESOLVED'
            """, (user_id,))
            user_medium = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total 
                FROM tickets 
                WHERE created_by=%s AND priority='LOW' AND status != 'RESOLVED'
            """, (user_id,))
            user_low = cursor.fetchone()["total"]

            # Tickets recientes del usuario
            cursor.execute("""
                SELECT t.id, t.title, t.status, t.priority, t.created_at, 
                       a.name AS assigned_to_name
                FROM tickets t
                LEFT JOIN users a ON t.assigned_to = a.id
                WHERE t.created_by = %s
                ORDER BY t.created_at DESC
                LIMIT 10
            """, (user_id,))
            user_recent_tickets = cursor.fetchall()

            stats = {
                "total_user_tickets": total_user_tickets,
                "user_open": user_open,
                "user_in_progress": user_in_progress,
                "user_resolved": user_resolved,
                "user_high": user_high,
                "user_medium": user_medium,
                "user_low": user_low,
                "user_recent_tickets": user_recent_tickets
            }

    conn.close()

    return render_template('dashboard.html', stats=stats, user_role=user_role)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("Email already registered.", "warning")
                return redirect(url_for('login'))

            cursor.execute("""
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
            """, (name, email, password_hash))
        
        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            # Store user info in session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash("Welcome, {}!".format(user['name']), "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route('/tickets')
@login_required
def tickets_list():
    user_id = session["user_id"]
    user_role = session["user_role"]
    
    # Obtener parámetros de filtro
    order = request.args.get('order', 'asc')  # 'asc' o 'desc'
    status_filter = request.args.get('status', 'all')  # 'all', 'OPEN', 'IN_PROGRESS', 'RESOLVED'
    priority_filter = request.args.get('priority', 'all')  # 'all', 'LOW', 'MEDIUM', 'HIGH'
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Construir las cláusulas WHERE para los filtros
        status_condition = ""
        if status_filter != 'all':
            status_condition = f"AND t.status = '{status_filter}'"
        
        priority_condition = ""
        if priority_filter != 'all':
            priority_condition = f"AND t.priority = '{priority_filter}'"
        
        # Construir la cláusula ORDER BY
        order_clause = "ASC" if order == 'asc' else "DESC"
        
        if user_role == "ADMIN":
            query = f"""
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                LEFT JOIN users a ON t.assigned_to = a.id
                WHERE 1=1 {status_condition} {priority_condition}
                ORDER BY t.created_at {order_clause}
            """
            cursor.execute(query)
        elif user_role == "AGENT":
            query = f"""
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                LEFT JOIN users a ON t.assigned_to = a.id
                WHERE (t.assigned_to = %s OR t.assigned_to IS NULL) {status_condition} {priority_condition}
                ORDER BY t.created_at {order_clause}
            """
            cursor.execute(query, (user_id,))
        else:   # USER
            query = f"""
                SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                LEFT JOIN users a ON t.assigned_to = a.id
                WHERE t.created_by = %s {status_condition} {priority_condition}
                ORDER BY t.created_at {order_clause}
            """
            cursor.execute(query, (user_id,))

        tickets = cursor.fetchall()

    conn.close()
    return render_template('tickets_list.html', 
                         tickets=tickets, 
                         user_role=user_role,
                         current_order=order,
                         current_status=status_filter,
                         current_priority=priority_filter)

@app.route('/tickets/new', methods=['GET', 'POST'])
@login_required
def ticket_new():
    if request.method == 'POST':
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority")
        created_by = session["user_id"]

        if not title or not description:
            flash("Title and/or description are required.", "warning")
            return redirect(url_for('ticket_new'))

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, created_by)
                VALUES (%s, %s, %s, %s)
            """, (title, description, priority, created_by))  
        
        conn.commit()
        conn.close()

        flash("Ticket created successfully.", "success")
    return render_template("ticket_new.html")

@app.route('/tickets/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
            FROM tickets t
            JOIN users u ON t.created_by = u.id
            LEFT JOIN users a ON t.assigned_to = a.id
            WHERE t.id = %s
        """, (ticket_id,))
        ticket = cursor.fetchone()

        cursor.execute("""
            SELECT c.*, u.name AS user_name
            FROM ticket_comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.ticket_id = %s
            ORDER BY c.created_at ASC
        """, (ticket_id,))
        comments = cursor.fetchall()

        cursor.execute("SELECT id, name FROM users WHERE role IN ('ADMIN', 'AGENT')")
        agents = cursor.fetchall()
    conn.close()

    if not ticket:
        flash("Ticket not found.", "danger")
        return redirect(url_for('tickets_list'))
    
    return render_template('ticket_detail.html', 
                            ticket=ticket, 
                            comments=comments,
                            agents=agents)
    
@app.route("/tickets/<int:ticket_id>/update", methods=["POST"])
@login_required
def ticket_update(ticket_id):
    user_role = session["user_role"]
    if user_role not in ["ADMIN", "AGENT"]:
        flash("You do not have permission to update tickets.", "danger")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))
    
    status = request.form.get("status")
    assigned_to = request.form.get("assigned_to") or None

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE tickets
            SET status=%s, assigned_to=%s
            WHERE id=%s
        """, (status, assigned_to, ticket_id))

    conn.commit()
    conn.close()

    flash("Ticket updated.", "success")
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))

@app.route("/tickets/<int:ticket_id>/comments", methods=["POST"])
@login_required
def comment_add(ticket_id):
    comment_text = request.form.get("comment")
    user_id = session["user_id"]

    if not comment_text:
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO ticket_comments (ticket_id, user_id, comment)
            VALUES (%s, %s, %s)
        """, (ticket_id, user_id, comment_text))
    
    conn.commit()
    conn.close()
    
    flash("Comment added.", "success")
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


@app.route('/users')
@login_required
@role_required(['ADMIN'])
def users_list():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
    conn.close()
    return render_template('users_list.html', users=users)

@app.route("/users/<int:user_id>/role", methods=["POST"])
@login_required
@role_required(['ADMIN'])
def user_change_role(user_id):
    new_role = request.form.get("role")
    if new_role not in ["ADMIN", "AGENT", "USER"]:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"success": False, "message": "Invalid role."}, 400
        flash("Invalid role.", "danger")
        return redirect(url_for("users_list"))
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Obtener el nombre del usuario para la respuesta
        cursor.execute("SELECT name FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        
        cursor.execute("UPDATE users SET role=%s WHERE id=%s", (new_role, user_id))
    conn.commit()
    conn.close()

    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {
            "success": True, 
            "message": f"Role updated successfully for {user['name'] if user else 'user'}",
            "new_role": new_role
        }, 200
    
    flash("Role updated.", "success")
    return redirect(url_for("users_list"))

if __name__ == '__main__':
    app.run(debug=False)