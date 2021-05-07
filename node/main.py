from multiprocessing import Process
from grapevine.main import main as network

class FullNode(Process):
    """
    """
    def __init__(self):
        Process.__init__(self)
        network()


if __name__ == '__main__':
    node = FullNode()
    