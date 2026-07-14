import sys
class CustomException(Exception):
    def __init__(self,error_message,error_detail:sys):
        self.error_messages=error_message
        _,_,exc_tb=error_detail.exc_info()
        self.lineno=exc_tb.tb_lineno
        self.filename=exc_tb.tb_frame.f_code.co_filename
    def  __str__(self):
       return "Error occured in python script name [{0}] at line number [{1}] error message [{2}]".format(self.filename,self.lineno,self.error_messages)