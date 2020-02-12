import logging
import yaml
from deepdiff import DeepDiff
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.ProfileDiff import ProfileDiffStruct

logger = logging.getLogger("content-test-filtering.diff_analysis")

# Not to test changes
FILTER_LIST = ["root['documentation_complete']", "root['title']",
    "root['description']"]

class ProfileAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = ProfileDiffStruct(self.absolute_path)
        path = self.filepath.split("/")
        # format: PRODUCT/profiles/PROFILE.profile
        self.product = path[0]
        self.profile = path[-1].split(".")[0]

    def iterate_changed_rules(self, items):
        items_list = []

        for key, value in items:
            if "root['selections']" in key:
                items_list.append(value)

        return items_list

    def item_added(self, items):
        self.add_profile_information()
        self.diff_struct.added_rules.update(self.iterate_changed_rules(items))

    def item_removed(self, items):
        self.add_profile_information()
        self.diff_struct.removed_rules.update(self.iterate_changed_rules(items))

    def check_changed_values(self, items):
        for key in items:
            if "root['selections']" in key:
                self.diff_struct.added_rules.update(self.iterate_changed_rules(items))

    def add_profile_information(self):
        # Already defined for the file
        if self.diff_struct.product is not None and \
            self.diff_struct.profile is not None:
            pass

        self.diff_struct.product = self.product
        self.diff_struct.profile = self.profile

    def dict_added(self, items):
        if len(items) != len(set(items) & set(FILTER_LIST)):
            self.add_profile_information()

    def dict_removed(self, items):
        if len(items) != len(set(items) & set(FILTER_LIST)):
            self.add_profile_information()

    def type_changed(self, items):
        self.add_profile_information()

    def process_analysis(self):
        logger.info("Analyzing profile file " + self.filepath)

        # New profile was added to product - test profile and all rules in it
        if self.file_flag == 'A':
            logger.info("New profile " + self.profile + " was added.")
            new_profile = yaml.safe_load(self.content_after)
            try:
                rules = new_profile["selections"]
                self.diff_struct.added_rules = rules 
            except KeyError:
                logger.info("New profile doesn't contain any rule.")

            self.add_profile_information()
            return
        # Profile was removed - nothing to test
        elif self.file_flag == 'D':
            logger.info("Profile " + self.profile + " was removed.")
            return

        # Load previous and new profile
        yaml_before = yaml.safe_load(self.content_before)
        yaml_after = yaml.safe_load(self.content_after)

        # Find differencies in two dictionaries and ignore order
        deep_diff = DeepDiff(yaml_before, yaml_after, ignore_order=True)

        # Some key was added/removed/changed - need to validate the
        # profile with basic profile test
        if "dictionary_item_added" in deep_diff:
            self.dict_added(deep_diff["dictionary_item_added"])
        if "dictionary_item_removed" in deep_diff:
            self.dict_removed(deep_diff["dictionary_item_removed"])
        if "type_changes" in deep_diff:
            self.type_changed(deep_diff["type_changes"])

        # Check what values got changed
        if "values_changed" in deep_diff:
            values_changed = deep_diff["values_changed"].keys()
            self.check_changed_values(values_changed)

        # If an iterable was added/removed, it is important change for profile
        if "iterable_item_added" in deep_diff:
            self.item_added(deep_diff["iterable_item_added"].items())

        if "iterable_item_removed" in deep_diff:
            self.item_removed(deep_diff["iterable_item_removed"].items())

        logger.info("Added rules to profile: %s", " ".join(self.diff_struct.added_rules))
        logger.info("Removed rules to profile: %s", " ".join(self.diff_struct.removed_rules))
