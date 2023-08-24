from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc
import ssl
from decimal import Decimal
app = Flask(__name__)
CORS(app)

# Conexión a la base de datos
server = 'SERVER'  # Nombre del servidor
database = 'HCONCORDIA'  # Nombre de la base de datos
username = 'sa'  # Nombre de usuario
password = 'Sxg5dba123*'  # Contraseña
conn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')

# Obtener nombre y entidad por número de cédula


@app.route('/clientes/<int:cedula>', methods=['GET'])
def get_cliente(cedula):
    cursor = conn.cursor()
    cedula_str = str(cedula)
    query = "select *from VIQ_APICITAS where ID LIKE  '%" + cedula_str + "%'"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()

    if result:
        cliente = {
            "Nombre": result.Nombre,
            "Entidad": result.Entidad,
            "ID": result.ID
        }
        return jsonify(cliente)
    else:
        conn.close()
        return jsonify({"message": "Cliente no encontrado"}), 404

# Consultar cliente por ID


@app.route('/clientes', methods=['GET'])
def consultar_cliente():
    id = request.args.get('id')
    if id:
        cursor = conn.cursor()
        query = "select *from VIQ_APICITAS where ID LIKE  '%" + id + "%'"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()

        if result:
            cliente = {
                "Nombre": result.Nombre,
                "Entidad": result.Entidad,
                "ID": result.ID
            }
            return jsonify(cliente)
        else:
            return jsonify({"message": "Usuario no tiene ficha creada en el hospital. Es necesario que se acerque personalmente a nuestras instalaciones a realizar la solicitud de cita"}), 404
    else:
        return app.send_static_file('formulario.html')

# Consultar médicos disponibles según el query proporcionado


@app.route('/medicos_disponibles', methods=['GET'])
def consultar_medicos_disponibles():
    fecha = request.args.get('fecha')

    # Si la fecha contiene caracteres no numéricos, elimínalos
    fecha = ''.join(filter(str.isdigit, fecha))

    # Convierte la fecha a un valor entero
    try:
        fecha_int = int(fecha)
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido"}), 400

    cursor = conn.cursor()
    query = f" SELECT *FROM VIQ_APIMEDICOS WHERE FECHA > '{fecha_int}'  "
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    if results:
        medicos_disponibles = []
        for result in results:
            # Convertir el resultado en un diccionario para acceder a los campos por nombre
            medico = {
                "NOMBRE PROFESIONAL": result[0],
                "NOMBRE ESPECIALIDAD": result[1],
                "FECHA": result[2],
                "HORA1": result[3],
                "CODIGO CLIENTE": result[4],
                "NOMBRE CLIENTE": result[5],
                "ACTIVIDAD": result[6]
            }
            medicos_disponibles.append(medico)

        return jsonify(medicos_disponibles)
    else:
        return jsonify({"message": "No hay médicos disponibles"}), 404


if __name__ == '__main__':
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(debug=True, host='0.0.0.0', port=9000, ssl_context=context)
