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
            return jsonify({"message": "usuarion o no tiene ficha creada en el hospital, es necesrio que se acerque personalmente a nuestras instalaciones a realizar la solicitud de cita"}), 404
    else:
        return app.send_static_file('formulario.html')

if __name__ == '__main__':
       context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
       context.load_cert_chain('cert.pem', 'key.pem')
       app.run(debug=True, host='0.0.0.0', port=9000, ssl_context=context)
