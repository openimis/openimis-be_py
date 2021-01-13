from waitress import serve

from openIMIS.wsgi import application

if __name__ == '__main__':
    serve(application, listen='0.0.0.0:8000')
