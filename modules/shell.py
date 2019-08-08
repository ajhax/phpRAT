class shell:
    def __init__(self):
        self.name = 'shell'
        self.machine_id = None
        self.command = None

    @property
    def options(self):
        return [('machine_id', self.machine_id, 'True'),
                ('command', self.command, 'True')]
