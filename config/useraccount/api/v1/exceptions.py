from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError



class NoExistingUser(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {"detail": "No user account found."}
    default_code = 'no user'


class InactiveUser(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {"detail": "Account is not active."}
    default_code = 'inactive user'