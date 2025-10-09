
class NFeedException(Exception):
    def __init__(self, message,code=500):
        super(NFeedException,self).__init__(message)
        self.code=code

class GeneralException(NFeedException):
    def __init__(self, message, code=500):
        super(GeneralException,self).__init__(message, code) 

class InputException(NFeedException):
    def __init__(self, message, code=500):
        super(InputException,self).__init__(message, code) 

class TokenException(NFeedException):
    def __init__(self, message, code=500):
        super(TokenException,self).__init__(message, code)

class MiraeException(NFeedException):
    def __init__(self, message, code=500):
        super(MiraeException,self).__init__(message, code)

class DataException(NFeedException):
    def __init__(self, message, code=502):
        super(DataException, self).__init__(message, code)

class APIKeyException(NFeedException):
    def __init__(self, message, code=500):
        super(APIKeyException,self).__init__(message, code) 

        

