class SimuluxDiskException(BaseException):
    def __init__(self, args):
        self.args = args
        
