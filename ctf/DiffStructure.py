class DiffFileType:
    PROFILE = 1
    PYTHON = 2


class DiffStructure:
    def __init__(self, file_name=None):
        self.file_name = None
        self.diff_type = None
        self.rules_removed = []
