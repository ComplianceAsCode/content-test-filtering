from abc import ABC, abstractmethod


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


class ChangeType:
    NOT_IMPORTANT = 1
    IMPORTANT = 2
    OTHER = 3


class AbstractDiffStruct(ABC):
    def __init__(self):
        self.diff_type = None
        self.change_type = ChangeType.OTHER
        self.filepath = None
        self.affected_entities = {}

    def __repr__(self):
        return self.diff_type

    @abstractmethod
    def compute_dependencies(self):
        pass


class ProfileDiffStruct(AbstractDiffStruct):
    def __init__(self):
        super(ProfileDiffStruct, self).__init__()
        self.diff_type = DiffFileType.PROFILE
        self.product = None
        self.profile = None
        self.rules_added = []
        self.rules_removed = []

    def compute_dependencies(self):
        if self.change_type is ChangeType.IMPORTANT or \
                self.change_type is ChangeType.OTHER:
            self.add_affected_profile()

        if self.change_type is ChangeType.IMPORTANT:
            self.add_affected_product()

    def add_affected_product(self):
        if self.product is ProductType.RHEL6:
            self.affected_entities["product"] = "rhel6"
        elif self.product is ProductType.RHEL7:
            self.affected_entities["product"] = "rhel7"
        elif self.product is ProductType.RHEL8:
            self.affected_entities["product"] = "rhel8"

    def add_affected_profile(self):
        if self.profile is ProfileType.OSPP:
            self.affected_entities["profile"] = "ospp"

class PythonDiffStruct(AbstractDiffStruct):
    pass


class BashDiffStruct(AbstractDiffStruct):
    pass
