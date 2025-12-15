from werkzeug.security import generate_password_hash

# Generar el hash de la contraseña para el administrador
password = "admin123"
hashed_password = generate_password_hash(password)

print("Hashed password: ", hashed_password)