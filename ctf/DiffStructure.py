from abc import ABC


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


class AbstractDiffStruct(ABC):
    def __init__(self):
        self.diff_type = None
        self.filepath = None
        self.change_type = None
        self.affected_entities = []

    def __repr__(self):
        return self.diff_type


class ProfileDiffStruct(AbstractDiffStruct):
    def __init__(self):
        super(ProfileDiffStruct, self).__init__()
        self.diff_type = DiffFileType.PROFILE
        self.product = None
        self.profile = None
        self.rules_added = []
        self.rules_removed = []


class PythonDiffStruct(AbstractDiffStruct):
    pass


class BashDiffStruct(AbstractDiffStruct):
    pass
