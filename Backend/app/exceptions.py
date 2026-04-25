# File to handle custom exceptions fro the app. Allowing fro cleaner code.

class AppError(Exception):
  def __init__(self, message, status_code):
    super().__init__(message)
    self.message = message
    self.status_code = status_code
  
class BadRequestError(AppError):
  # Always 400
  def __init__(self, message):
    super().__init__(message, 400)
    

class UnauthorisedError(AppError):
  # Always 401
  def __init__(self, message):
    super().__init__(message, 401)

class ForbiddenError(AppError):
  # Always 403
  def __init__(self, message):
    super().__init__(message, 403)

class NotFoundError(AppError):
  # Always 404
  def __init__(self, message):
    super().__init__(message, 404)

