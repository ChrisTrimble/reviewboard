class OwnershipError(ValueError):
    pass


class PermissionError(Exception):
    def __init__(self):
        Exception.__init__(self, None)

class HttpResponseNotAuthorized(Exception):
    status_code = 401

    def __init__(self, error_message = None):
        Exception.__init__(self, error_message)
        