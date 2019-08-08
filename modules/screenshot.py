class screenshot:
    def __init__(self):
        self.name = 'screenshot'
        self.machine_id = None

    @property
    def options(self):
        return [('machine_id', self.machine_id, 'True')]
