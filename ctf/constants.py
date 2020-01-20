class FileType:
    PROFILE = 1
    PYTHON = 2
    YAML = 3


class ProductType:
    OTHER       = 0
    CHROMIUM    = 1
    DEBIAN10    = 2
    DEBIAN8     = 3
    DEBIAN9     = 4
    EAP6        = 5
    FEDORA      = 6
    FIREFOX     = 7
    FUSE6       = 8
    JRE         = 9
    OCP3        = 10
    OCP4        = 11
    OL7         = 12
    OL8         = 13
    OPENSUSE    = 14
    RHEL6       = 15
    RHEL7       = 16
    RHEL8       = 17
    RHOSP10     = 18
    RHOSP13     = 19
    RHV4        = 20
    SLE11       = 21
    SLE12       = 22
    UBUNTU1404  = 23
    UBUNTU1604  = 24
    UBUNTU1804  = 25
    UBUNTU1019  = 26
    WRLINUX1019 = 26
    WRLINUX8    = 28


PRODUCT_TYPE = {
    "unknown": ProductType.OTHER,
    "chromium": ProductType.CHROMIUM,
    "debian10": ProductType.DEBIAN10,
    "debian8": ProductType.DEBIAN8,
    "debian9": ProductType.DEBIAN9,
    "eap6": ProductType.EAP6,
    "fedora": ProductType.FEDORA,
    "firefox": ProductType.FIREFOX,
    "fuse6": ProductType.FUSE6,
    "ocp3": ProductType.OCP3,
    "ocp4": ProductType.OCP4,
    "ol7": ProductType.OL7,
    "ol8": ProductType.OL8,
    "opensuse": ProductType.OPENSUSE,
    "rhel6": ProductType.RHEL6,
    "rhel7": ProductType.RHEL7,
    "rhel8": ProductType.RHEL8
}


class ProfileType:
    OTHER      = 0
    CJIS       = 1
    CUI        = 2
    E8         = 3
    HIPAA      = 4
    OSPP_MLS   = 5
    OSPP       = 6
    PCI_DSS    = 7
    RHELH_STIG = 8
    RHELH_VPP  = 9
    RHT_CPP    = 10
    STANDARD   = 11
    STIG       = 12


PROFILE_TYPE = {
    "unknown": ProfileType.OTHER,
    "cjis": ProfileType.CJIS,
    "cui": ProfileType.CUI,
    "e8": ProfileType.E8,
    "hipaa": ProfileType.HIPAA,
    "ospp-mls": ProfileType.OSPP_MLS,
    "ospp": ProfileType.OSPP,
    "pci-dss": ProfileType.PCI_DSS,
    "rhelh-stig": ProfileType.RHELH_STIG,
    "rhelh-vpp": ProfileType.RHELH_VPP,
    "rht-cpp": ProfileType.RHT_CPP,
    "standard": ProfileType.STANDARD,
    "stig": ProfileType.STIG
}


class ChangeType:
    NOT_IMPORTANT = 1
    IMPORTANT = 2
    OTHER = 3