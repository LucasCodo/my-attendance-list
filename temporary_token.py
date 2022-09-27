from datetime import datetime, timedelta
from secrets import token_hex
import pyqrcode


class Token():
    def __init__(self,n_bytes=32,seconds = 10, alive = True):
        self.key = token_hex(n_bytes)
        self.duration = seconds
        self.due_date = datetime.now()+timedelta(seconds = seconds)
        self.alive = alive
        pass
    def is_valid(self):
        if datetime.now()>self.due_date:
            self.alive = False
        return self.alive
    @property
    def qr_code(self):
        return pyqrcode.create(self.key)
    @property
    def base64_qr_code(self,scale=6):
        return self.qr_code.png_as_base64_str(scale=scale)
    def __iter__(self):
        yield self.key,self
    def __str__(self):
        return self.key

if __name__=="__main__":
    dic = {}
    for t in range(10):
        dic.update(Token())
    #print(t.base64_qr_code)
    #print(t.is_valid())
    
