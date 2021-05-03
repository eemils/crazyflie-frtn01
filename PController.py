import threading

class PController:
    def __init__(self, h):
        # Private variables
        self.v = 0 # Output from controller

        # Control variables
        self.K = 35768
        self.beta = 1
        self.h = h # period in ms

        self._lock = threading.Lock()

    def calc_out(self, y, y_ref):
        with self._lock:
            # Calculate output
            self.v = self.K*(self.beta*y_ref-y)#39250
        return int(self.v)

    def set_params(self, **kwargs):
        with self._lock:
            self.K = kwargs.get('K', self.K)
            self.beta = kwargs.get('beta', self.beta)
            self.h = kwargs.get('h',self.h)
