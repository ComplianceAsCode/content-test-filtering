import logging
import yaml
from deepdiff import DeepDiff
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.DiffStructure import ProfileDiffStruct, ProductType, PRODUCT_TYPE, \
                            ProfileType, PROFILE_TYPE, ChangeType

logger = logging.getLogger("content-test-filtering.diff_analysis")


class ProfileAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_structure = ProfileDiffStruct()
        self.calculate_properties()

    def calculate_properties(self):
        #self._filepath = path
        path = self.filepath.split("/")
        try:
            self.diff_structure.product = PRODUCT_TYPE[path[0]]
        except KeyError:
            self.diff_structure.product = PRODUCT_TYPE["unknown"]

        profile_file = path[-1]
        profile = profile_file.split(".")[0]
        try:
            self.diff_structure.profile = PROFILE_TYPE[profile]
        except KeyError:
            self.diff_structure.profile = PROFILE_TYPE["unknown"]

    def iterate_changed_rules(self, items):
        items_list = []
        self.diff_structure.change_type = ChangeType.IMPORTANT

        for key, value in items:
            if "root['selections']" in key:
                items_list.append(value)

        return items_list

    def item_added(self, items):
        self.diff_structure.rules_added = self.iterate_changed_rules(items)

    def item_removed(self, items):
        self.diff_structure.rules_removed = self.iterate_changed_rules(items)

    def check_changed_values(self, items):
        for key, value in items:
            if "root['documentation_complete']" in key or \
                    "root['description']" in key or \
                    "root['title']" in key:
                self.diff_structure.change_type = ChangeType.NOT_IMPORTANT
            elif "root['selections']" in key:
                rules_changed = self.iterate_changed_rules(items)

    def process_analysis(self):
        logger.info("Analyzing profile file " + self.filepath)

        data_map_before = yaml.safe_load(self.content_before)
        data_map_after = yaml.safe_load(self.content_after)

        # Find differencies in two dictionaries
        deep_diff = DeepDiff(data_map_before, data_map_after, ignore_order=True)

        # Check what values got changed - in this case it can be
        # changed description/documentation_complete/title
        if "values_changed" in deep_diff:
            values_changed = deep_diff["values_changed"].keys()
            self.check_changed_values(values_changed)

        # If an iterable was added/removed, it is important change for profile
        if "iterable_item_added" in deep_diff:
            self.item_added(deep_diff["iterable_item_added"].items())
        if "iterable_item_removed" in deep_diff:
            self.item_removed(deep_diff["iterable_item_removed"].items())

        logger.info("Added rules - %s", self.diff_structure.rules_added)
        logger.info("Removed rules - %s", self.diff_structure.rules_removed)
