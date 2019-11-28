class DiffFileType:
    PROFILE = 1
    PYTHON = 2

class ProductType:
    RHEL6 = 1
    RHEL7 = 2
    RHEL8 = 3
    OTHER = 4

class ProfileType:
    OSPP = 1
    PCI_DSS = 2
    NCP = 3
    DISA_STIG = 4
    OTHER = 5

class DiffStructure:
    def __init__(self, file_name=None):
        self.diff_type = None
        self.filepath = None
        self.file_name = None
        self.product = None
        self.profile = None
        self.rules_added = []
        self.rules_removed = []
