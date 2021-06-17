

class Sequence:
    
    def __init__(self, init = 0):
        self.val = init
        
    def curval(self):
        return self.val
    
    def nextval(self):
        self.val += 1
        return self.val