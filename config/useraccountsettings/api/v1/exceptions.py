from rest_framework import status
from rest_framework.exceptions import APIException



class DeleteNotAllowed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"detail": "DELETE method is not allowed."}
    default_code = 'delete_not_allowed'


class PostNotAllowed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"detail": "DELETE method is not allowed."}
    default_code = 'delete_not_allowed'
