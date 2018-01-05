from adapter import Adapter


class TPLinkAdapter(Adapter):

    def __init__(self, verbose=False):
        self.name = self.__class__.__name__
        Adapter.__init__(self,
                         'tplink-adapter',
                         'tplink-adapter',
                         verbose=verbose)


if __name__ == '__main__':
    a = TPLinkAdapter(verbose=True)
