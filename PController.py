import threading

class PController:
    def __init__(self):
        # Private variables
        self.v = 0 # Output from controller

        # Control variables
        self.K = 2
        self.beta = 1
        self.h = 0.02 # period

        self._lock = threading.Lock()

    def calc_out(self, y, y_ref):
        with self._lock:
            # Calculate output
            self.v = self.K*(self.beta*y_ref-y)
        return self.v

    def set_params(self, **kwargs):
        with self._lock:
            self.K = kwargs.get('K', self.K)
            self.beta = kwargs.get('beta', self.beta)
            self.h = kwargs.get('h',self.h)
