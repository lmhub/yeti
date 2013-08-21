from django.contrib.auth.middleware import RemoteUserMiddleware

class SubjectDnAuthMiddleware(RemoteUserMiddleware):
    header = 'SSL_CLIENT_S_DN'