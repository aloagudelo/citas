from ApiCitas import app
from waitress import serve

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=9000, url_scheme='https', certfile='/Apicitas/cert.pem', keyfile='/Apicitas/key.pem')
