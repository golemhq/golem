from . import common


class GolemExtendedDriver:

    def find(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['element'] = args[0]
        return common._find(self, **kwargs)

    def find_all(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['element'] = args[0]
        return common._find_all(self, **kwargs)

    def navigate(self, url):
        self.get(url)