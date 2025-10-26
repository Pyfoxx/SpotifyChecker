
class TokenExpired(Exception):
    def __init__(self):
        # super().__init__(message)
        self.error = 'The token has expired'

class RefreshExpired(Exception):
    def __init__(self):
        self.error = 'The refresh token has expired'

class InvalidToken(Exception):
    def __init__(self):
        self.error = 'Invalid token'