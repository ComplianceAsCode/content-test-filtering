import logging
import yaml
from deepdiff import DeepDiff
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.DiffStructure import ProfileDiffStruct, ProductType, ProfileType

logger = logging.getLogger("content-test-filtering.diff_analysis")


class ProfileAnalysis(AbstractAnalysis):
    def __init__(self, *args):
        super(ProfileAnalysis, self).__init__(*args)
        self.diff_structure = ProfileDiffStruct()

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, path):
        self._filepath = path
        path = self.filepath.split("/")
        # if path[0] == "rhel6":
        #     self.diff_structure.product = ProductType.RHEL6
        # elif path[0] == "rhel7":
        #     self.diff_structure.product = ProductType.RHEL7
        # elif path[0] == "rhel8":
        #     self.diff_structure.product = ProductType.RHEL8
        # else:
        #     self.diff_structure.product = ProductType.OTHER

        # profile = path[-1].split(".")[0]
        # if profile == "ospp":
        #     self.diff_structure.profile = ProfileType.OSPP
        # elif profile == "pci-dss":
        #     self.diff_structure.profile = ProfileType.PCI_DSS
        # elif profile == "ncp":
        #     self.diff_structure.profile = ProfileType.NCP
        # elif profile == "disa-stig":
        #     self.diff_structure.profile = ProfileType.DISA_STIG
        # else:
        #     self.diff_structure.profile = ProfileType.OTHER

    def iterate_profile(self, items):
        items_list = []
        print(items)

        for key, value in items:
            if "root['selections']" in key:
                items_list.append(value)

        return items_list

    def item_added(self, items):
        self.diff_structure.rules_added = self.iterate_profile(items)

    def item_removed(self, items):
        self.diff_structure.rules_removed = self.iterate_profile(items)

    def process_analysis(self):
        logger.info("Analyzing profile file " + self.filepath)

        data_map_before = yaml.safe_load(self.content_before)
        data_map_after = yaml.safe_load(self.content_after)
        deep_diff = DeepDiff(data_map_before, data_map_after, ignore_order=True)

        if "iterable_item_added" in deep_diff:
            self.item_added(deep_diff["iterable_item_added"].items())
        if "iterable_item_removed" in deep_diff:
            self.item_removed(deep_diff["iterable_item_removed"].items())

        logger.info("Added rules - ")
        print(self.diff_structure.rules_added)
        logger.info("Removed rules - ")
        print(self.diff_structure.rules_removed)
