from flask import Flask, jsonify, request, escape
from flask_cors import CORS
import pyodbc
import ssl
from decouple import config

app = Flask(__name__)
CORS(app)

# Conexión a la base de datos
server = config('DB_SERVER', default='X')
database = config('DB_DATABASE', default='X')
username = config('DB_USERNAME', default='X')
password = config('DB_PASSWORD', default='X')
conn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')

# Función para escapar datos y prevenir XSS
def escape_data(data):
    return escape(data)

# Manejo de errores personalizado
@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f"Error: {error}")
    return jsonify({"message": "Ocurrió un error en el servidor"}), 500

# Obtener nombre y entidad por número de cédula
@app.route('/clientes/<int:cedula>', methods=['GET'])
def get_cliente(cedula):
    try:
        cursor = conn.cursor()
        cedula_str = str(cedula)
        query = "SELECT * FROM VIQ_APICITAS WHERE ID LIKE ?"
        cursor.execute(query, ('%' + cedula_str + '%',))
        result = cursor.fetchone()
        cursor.close()

        if result:
            cliente = {
                "Nombre": escape_data(result.Nombre),
                "Entidad": escape_data(result.Entidad),
                "ID": escape_data(result.ID)
            }
            return jsonify(cliente)
        else:
            conn.close()
            return jsonify({"message": "Cliente no encontrado"}), 404
    except Exception as e:
        app.logger.error(f"Error en get_cliente: {e}")
        return jsonify({"message": "Ocurrió un error en el servidor"}), 500

# Consultar cliente por ID
@app.route('/clientes', methods=['GET'])
def consultar_cliente():
    try:
        id = request.args.get('id')
        if id:
            cursor = conn.cursor()
            query = "SELECT * FROM VIQ_APICITAS WHERE ID LIKE ?"
            cursor.execute(query, ('%' + id + '%',))
            result = cursor.fetchone()
            cursor.close()

            if result:
                cliente = {
                    "Nombre": escape_data(result.Nombre),
                    "Entidad": escape_data(result.Entidad),
                    "ID": escape_data(result.ID)
                }
                return jsonify(cliente)
            else:
                return jsonify({"message": "Usuario no tiene ficha creada en el hospital. Es necesario que se acerque personalmente a nuestras instalaciones a realizar la solicitud de cita"}), 404
        else:
            return app.send_static_file('formulario.html')
    except Exception as e:
        app.logger.error(f"Error en consultar_cliente: {e}")
        return jsonify({"message": "Ocurrió un error en el servidor"}), 500

# Consultar médicos disponibles según el query proporcionado
@app.route('/medicos_disponibles', methods=['GET'])
def consultar_medicos_disponibles():
    try:
        fecha = request.args.get('fecha')

        # Si la fecha contiene caracteres no numéricos, elimínalos
        fecha = ''.join(filter(str.isdigit, fecha))

        # Convierte la fecha a un valor entero
        try:
            fecha_int = int(fecha)
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido"}), 400

        cursor = conn.cursor()
        query = f"SELECT * FROM VIQ_APIMEDICOS WHERE FECHA > ?"
        cursor.execute(query, (fecha_int,))
        results = cursor.fetchall()
        cursor.close()

        if results:
            medicos_disponibles = []
            for result in results:
                medico = {
                    "NOMBRE PROFESIONAL": escape_data(result[0]),
                    "NOMBRE ESPECIALIDAD": escape_data(result[1]),
                    "FECHA": result[2],
                    "HORA1": result[3],
                    "CODIGO CLIENTE": result[4],
                    "NOMBRE CLIENTE": escape_data(result[5]),
                    "ACTIVIDAD": escape_data(result[6])
                }
                medicos_disponibles.append(medico)

            return jsonify(medicos_disponibles)
        else:
            return jsonify({"message": "No hay médicos disponibles"}), 404
    except Exception as e:
        app.logger.error(f"Error en consultar_medicos_disponibles: {e}")
        return jsonify({"message": "Ocurrió un error en el servidor"}), 500

if __name__ == '__main__':
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(debug=True, host='0.0.0.0', port=config('PORT'), ssl_context=context)
