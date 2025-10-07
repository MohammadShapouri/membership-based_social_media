from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError



class NoExistingConnection(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {"detail": "No user account connection found."}
    default_code = 'no user'
