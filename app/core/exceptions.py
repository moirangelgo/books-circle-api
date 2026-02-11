class BaseAppException(Exception):
    """Base class for application exceptions."""
    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)

class ItemNotFound(BaseAppException):
    """Raised when an item is not found."""
    pass

class ItemAlreadyExists(BaseAppException):
    """Raised when an item already exists."""
    pass

class DatabaseError(BaseAppException):
    """Raised when a database error occurs."""
    pass
