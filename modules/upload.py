class upload:
    def __init__(self):
        self.name = 'upload'
        self.machine_id = None
        self.path = None

    @property
    def options(self):
        return [('machine_id', self.machine_id, 'True'),
                ('path', self.path, 'True')]
