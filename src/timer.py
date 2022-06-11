# Measures time taken for a function execution, need to use lambda for the function argument
from datetime import datetime

class Timer:
    def start(self, identity:str='foo'):
        self.identity = identity
        self.start_t = datetime.now()
    def stop(self):
        t2 = datetime.now()
        print(f'Elapsed time :: {self.identity:12} :: {(t2-self.start_t).total_seconds():8.3f} s' )
