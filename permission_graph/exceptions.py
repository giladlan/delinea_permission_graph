class BasePermissionGraphException(Exception):
    pass

class ResourceNotFound(BasePermissionGraphException):
    pass

class InvalidResourceType(BasePermissionGraphException):
    pass