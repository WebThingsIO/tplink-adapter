from os import path
import sys
sys.path.append(path.join(path.dirname(path.abspath(__file__)), 'lib'))

from gateway_addon import Adapter


class TPLinkAdapter(Adapter):

    def __init__(self, verbose=False):
        self.name = self.__class__.__name__
        Adapter.__init__(self,
                         'tplink-adapter',
                         'tplink-adapter',
                         verbose=verbose)


if __name__ == '__main__':
    a = TPLinkAdapter(verbose=True)
