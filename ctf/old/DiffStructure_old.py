from abc import ABC, abstractmethod


class DiffFileType:
    PROFILE = 1
    PYTHON = 2
    ANSIBLE = 3


class ProductType:
    RHEL6 = 1
    RHEL7 = 2
    RHEL8 = 3
    OTHER = 4

PRODUCT_TYPE = {
    "rhel6": ProductType.RHEL6,
    "rhel7": ProductType.RHEL7,
    "rhel8": ProductType.RHEL8,
    "unknown": ProductType.OTHER
}


class ProfileType:
    OSPP = 1
    PCI_DSS = 2
    NCP = 3
    DISA_STIG = 4
    OTHER = 5

PROFILE_TYPE = {
    "ospp": ProfileType.OSPP,
    "pci-dss": ProfileType.PCI_DSS,
    "ncp": ProfileType.NCP,
    "disa-stig": ProfileType.DISA_STIG,
    "unknown": ProfileType.OTHER
}


class ChangeType:
    NOT_IMPORTANT = 1
    IMPORTANT = 2
    OTHER = 3


def find_product(rule_id):
    pass


class AbstractDiffStruct(ABC):
    def __init__(self):
        self.file_type = None
        self.change_type = ChangeType.OTHER
        self.filepath = None
        self.filename = None
        self.affected_entities = {}

    def __repr__(self):
        return self.file_type

    @abstractmethod
    def compute_dependencies(self):
        if self.file_type == DiffFileType.PROFILE or \
                self.file_type == DiffFileType.ANSIBLE:
            self.affected_entities["file_type"] = "yaml"


class ProfileDiffStruct(AbstractDiffStruct):
    def __init__(self):
        super().__init__()
        self.file_type = DiffFileType.PROFILE
        self.product = None
        self.profile = None
        self.rules_added = []
        self.rules_removed = []

    def compute_dependencies(self):
        super().compute_dependencies()
        if self.change_type is ChangeType.IMPORTANT or \
                self.change_type is ChangeType.OTHER:
            self.add_affected_profile()

        if self.change_type is ChangeType.IMPORTANT:
            self.add_affected_product()

        self.test_added_rules()

    def add_affected_product(self):
        self.affected_entities["product"] = list(PRODUCT_TYPE.keys())[
            list(PRODUCT_TYPE.values()).index(self.product)]

    def add_affected_profile(self):
        if self.profile is ProfileType.OSPP:
            self.affected_entities["profile"] = "ospp"

    def test_added_rules(self):
        self.affected_entities["rule_bash"] = self.rules_removed 


class AnsibleDiffStruct(AbstractDiffStruct):
    def __init__(self):
        super().__init__()
        self.file_type = DiffFileType.ANSIBLE
        self.rule = None

    def fill_dependencies(self):
        self.add_affected_entities()

    def add_affected_entities(self):
        self.affected_entities["rule_ansible"] = self.rule


class PythonDiffStruct(AbstractDiffStruct):
    pass


class BashDiffStruct(AbstractDiffStruct):
    pass
