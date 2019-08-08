class msg:
    def __init__(self):
        self.name = 'msg'
        self.machine_id = None
        self.message = None

    @property
    def options(self):
        return [('machine_id', self.machine_id, 'True'),
                ('message', self.message, 'True')]
