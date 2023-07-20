from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc
import ssl

app = Flask(__name__)
CORS(app)

# Conexión a la base de datos
server = 'SERVER'  # Nombre del servidor
database = 'HCONCORDIA'  # Nombre de la base de datos
username = 'sa'  # Nombre de usuario
password = 'Sxg5dba123*'  # Contraseña
conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')

# Obtener nombre y entidad por número de cédula
@app.route('/clientes/<int:cedula>', methods=['GET'])
def get_cliente(cedula):
    cursor = conn.cursor()
    cedula_str = str(cedula)
    query = f"SELECT ISNULL(KC_NOM,'') AS Nombre, ISNULL(ENT_NOMBRE,'') AS Entidad, KC_COD AS ID FROM TKCLIENTES LEFT JOIN TMUSUARIOSFACTURACION ON KC_COD = KC2_COD LEFT JOIN TMENTIDADES ON KC2_EPS_POS = ENT_COD WHERE KC_ZONA = '99' AND KC_COD LIKE '%" + cedula_str + "%'"
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
        query = f"SELECT ISNULL(KC_NOM,'') AS Nombre, ISNULL(ENT_NOMBRE,'') AS Entidad, KC_COD AS ID FROM TKCLIENTES LEFT JOIN TMUSUARIOSFACTURACION ON KC_COD = KC2_COD LEFT JOIN TMENTIDADES ON KC2_EPS_POS = ENT_COD WHERE KC_ZONA = '99' AND KC_COD like  '%" + id + "%'"
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
    fecha = request.args.get('fecha')  # Obtener el valor de la variable "fecha" de la URL
    
    cursor = conn.cursor()
    query = f"""
        SELECT 
            ISNULL(MED_NOMBRE, ' ') AS "NOMBRE PROFESIONAL",
            (SELECT ESP_NOMBRE FROM TMESPECIALIDADES WHERE MED_ESPECIALIDAD_1 = ESP_COD) AS "NOMBRE ESPECIALIDAD",
            ISNULL(TME2_FCH, 0) AS FECHA,
            CAST(TME2_HH AS VARCHAR) + ':' + CAST(TME2_MM AS VARCHAR) AS "HORA",
            ISNULL(TME2_COD, '') AS "CODIGO CLIENTE",
            ISNULL((SELECT TOP 1 KC_NOM FROM TKCLIENTES WHERE TME2_ZONA = KC_ZONA AND TME2_COD = KC_COD), '') AS "NOMBRE CLIENTE",
            TME2_ACTIVIDAD AS ACTIVIDAD
        FROM TMTURNOSMEDICOSDETALLE
        LEFT JOIN TMMEDICOS ON (TME2_CODM = MED_COD)
        WHERE TME2_FCH = '{fecha}' AND TME2_ACTIVIDAD = 90
    """
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
                "HORA": result[3],
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
