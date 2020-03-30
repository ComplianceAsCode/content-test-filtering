import os
import logging
import yaml
from deepdiff import DeepDiff
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.constants import FileType

logger = logging.getLogger("content-test-filtering.diff_analysis")

# Not to test changes
FILTER_LIST = ["root['documentation_complete']", "root['title']",
               "root['description']"]


class ProfileAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct.file_type = FileType.PROFILE
        path = self.filepath.split("/")
        # format: PRODUCT/profiles/PROFILE.profile
        self.product = path[0]
        self.profile = path[-1].split(".")[0]
        self.added_rules = []
        self.removed_rules = []
        self.test_already_added = False

    @staticmethod
    def can_analyse(filepath):
        if filepath.endswith(".profile"):
            return True
        return False

    def add_profile_test(self):
        if self.test_already_added:
            return
        self.test_already_added = True
        self.diff_struct.add_changed_profile(self.profile, self.product)
        self.find_dependent_profiles(self.diff_struct.absolute_path,
                                     self.profile)

    def is_rule(self, value):
        if "=" in value:
            logger.info("Value of %s variable in %s profile for %s changed.",
                        value.split("=")[0], self.profile, self.product)
            return False
        return True

    def iterate_changed_rules(self, items):
        items_list = []
        for key, value in items:
            if "root['selections']" in key:
                if self.is_rule(value):
                    items_list.append(value)
        return items_list

    def item_added(self, items):
        self.add_profile_test()
        self.added_rules.extend(self.iterate_changed_rules(items))

    def item_removed(self, items):
        self.add_profile_test()
        self.removed_rules.extend(self.iterate_changed_rules(items))

    def check_changed_values(self, items):
        for key in items:
            if "root['selections']" in key:
                self.add_profile_test()
                return

    def dict_added(self, items):
        if len(items) != len(set(items) & set(FILTER_LIST)):
            self.add_profile_test()

    def dict_removed(self, items):
        if len(items) != len(set(items) & set(FILTER_LIST)):
            self.add_profile_test()

    def type_changed(self):
        self.add_profile_test()

    def analyse_changes(self):
        # Load previous and new profile
        yaml_before = yaml.safe_load(self.content_before)
        yaml_after = yaml.safe_load(self.content_after)

        # Find differencies in two dictionaries and ignore order
        deep_diff = DeepDiff(yaml_before, yaml_after, ignore_order=True)

        for change_type, change in deep_diff.items():
            if change_type == "dictionary_item_added":
                self.dict_added(change)
            elif change_type == "dictionary_item_removed":
                self.dict_removed(change)
            elif change_type == "type_changes":
                self.type_changed()
            elif change_type == "values_changed":  # Check what value got changed
                values_changed = change.keys()
                self.check_changed_values(values_changed)
            # If an iterable was added/removed, it is important change for profile
            elif change_type == "iterable_item_added":
                self.item_added(change.items())
            elif change_type == "iterable_item_removed":
                self.item_removed(change.items())

    def new_profile_added(self):
        new_profile = yaml.safe_load(self.content_after)
        try:
            rules = new_profile["selections"]
            self.added_rules = rules
        except KeyError:
            logger.warning("New profile doesn't contain any rule.")
        self.add_profile_test()

    def find_dependent_profiles(self, absolute_path, profile):
        # No profile - no dependencies
        if not self.profile:
            return

        extended_profiles = []
        folder = os.path.dirname(absolute_path)
        # Look to profiles for same product
        for f in os.listdir(folder):
            # Not a profile file
            if not f.endswith(".profile"):
                continue

            filepath = folder + "/" + f
            with open(filepath, "r") as stream:
                # Load to dict
                try:
                    profile_file = yaml.safe_load(stream)
                except yaml.YAMLError as e:
                    print(e)

                # Try get which profile it extends
                try:
                    extends = profile_file["extends"]
                    if extends == profile:
                        extended_profiles.append(filepath)
                # Profile does not extend any other profile
                except KeyError:
                    pass

        # For each profile which is extended by changed profile
        # add it for testing and find which profiles they are extended by
        for f in extended_profiles:
            path = f.split("/")[-1]
            profile_name = path.split(".")[0]
            logger.info("%s profile extends %s.", profile_name.upper(), profile.upper())
            self.diff_struct.add_changed_profile(profile_name, self.product)
            self.find_dependent_profiles(f, profile_name)

    def process_analysis(self):
        logger.info("Analyzing profile %s for %s", self.profile.upper(), self.product)

        if self.is_added():
            self.new_profile_added()
            return self.diff_struct
        elif self.is_removed():
            return self.diff_struct

        self.analyse_changes()

        if self.added_rules:
            logger.info("Added rules to profile: %s",
                        " ".join(self.added_rules))
        if self.removed_rules:
            logger.info("Removed rules from profile: %s",
                        " ".join(self.removed_rules))

        return self.diff_struct
