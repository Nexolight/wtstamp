import logging

class Visualizer():
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        pass
    
    def saldo(self):
        self.l.info("Generating saldo visualization...")
    
    def month(self):
        self.l.info("Generating month visualization...")
    
    def week(self):
        self.l.info("Generating week visualization...")
    
    def last(self):
        self.l.info("Generating visualization from last closed workday...")
    
    def open(self):
        self.l.info("Generating visualization from currently open workday...")
    