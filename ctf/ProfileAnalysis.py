import logging
import yaml
from deepdiff import DeepDiff
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.ProfileDiff import ProfileDiffStruct
#from ctf.DiffStructure import ProfileDiffStruct, ProductType, PRODUCT_TYPE, \
#                            ProfileType, PROFILE_TYPE, ChangeType

logger = logging.getLogger("content-test-filtering.diff_analysis")

FILTER_LIST = ["root['documentation_complete']", "root['title']",
    "root['description']", "root['extends']"]

class ProfileAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = ProfileDiffStruct(self.file_path, self.file_name)
        path = self.file_path.split("/")
        # format: PRODUCT_NAME/profiles/PROFILE_NAME.profile
        self.diff_struct.product = path[0]
        self.diff_struct.profile = path[-1].split(".")[0]

    def calculate_properties(self):
        #self._filepath = path
        path = self.file_path.split("/")
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
            if "root['selections']" in key:
                rules_changed = self.iterate_changed_rules(items)
            else:
                return
            # "root['documentation_complete']" in key or \
            #        "root['description']" in key or \
            #        "root['title']" in key:

    def add_profile_tests(self):
        # already defined for the file
        if self.diff_struct.product is not None and \
            self.diff_struct.profile is not None:
            pass

        folders = self.diff_struct.file_path.split("/")
        profile_file = folders[-1]

        self.diff_struct.product = folders[0]
        self.diff_struct.profile = profile_file.split(".")[0]


    def dict_added(self, items):
        if len(items) == len(set(items) & set(FILTER_LIST)):
            self.add_profile_test()
        else:

            pass

    def dict_removed(self, items):
        pass

    def type_changed(self, items):
        pass


    def process_analysis(self):
        logger.info("Analyzing profile file " + self.diff_struct.file_path)

        # Load previous and new profile
        yaml_before = yaml.safe_load(self.content_before)
        yaml_after = yaml.safe_load(self.content_after)

        # Find differencies in two dictionaries and ignore order
        deep_diff = DeepDiff(yaml_before, yaml_after, ignore_order=True)

        # Some key was added/removed - need to validate the profile with build

        if "dictionary_item_added" in deep_diff:
            self.dict_added(deep_diff["dictionary_item_added"])
        
        if "dictionary_item_removed" in deep_diff:
            self.dict_removed(deep_diff["dictionary_item_removed"])

        if "type_changes" in deep_diff:
            self.type_changed(deep_diff["type_changes"])
        
        

        if "dictionary_item_added" in deep_diff or \
                "dictionary_item_removed" in deep_diff or \
                "type_changes" in deep_diff:
            self.diff_struct.products[self.product] = self.profile

        # Check what values got changed
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
