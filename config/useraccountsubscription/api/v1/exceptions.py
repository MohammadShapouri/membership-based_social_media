from rest_framework import status
from rest_framework.exceptions import APIException



class OnlyGetMethodAllowed(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {"detail": "Only 'GET' method is acceptable."}
    default_code = 'unavailable method'
