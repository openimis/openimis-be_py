from waitress import serve

from openIMIS.wsgi import application

if __name__ == '__main__':
    serve(application, listen='127.0.0.1:8000')
