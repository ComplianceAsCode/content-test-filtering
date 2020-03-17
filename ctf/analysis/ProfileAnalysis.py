import logging
import yaml
from deepdiff import DeepDiff
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.diffstruct.ProfileDiff import ProfileDiffStruct
from ctf.diff import git_wrapper


logger = logging.getLogger("content-test-filtering.diff_analysis")

# Not to test changes
FILTER_LIST = ["root['documentation_complete']", "root['title']",
    "root['description']"]


class ProfileAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = ProfileDiffStruct(self.filepath)
        path = self.filepath.split("/")
        # format: PRODUCT/profiles/PROFILE.profile
        self.product = path[0]
        self.profile = path[-1].split(".")[0]


    @staticmethod
    def is_valid(filepath):
        if filepath.endswith(".profile"):
            return True
        return False


    def iterate_changed_rules(self, items):
        items_list = []
        for key, value in items:
            if "root['selections']" in key:
                items_list.append(value)
        return items_list


    def item_added(self, items):
        self.add_profile_test(self.product, self.profile)
        self.diff_struct.added_rules.update(self.iterate_changed_rules(items))


    def item_removed(self, items):
        self.add_profile_test(self.product, self.profile)
        self.diff_struct.removed_rules.update(self.iterate_changed_rules(items))


    def check_changed_values(self, items):
        for key in items:
            if "root['selections']" in key:
                self.diff_struct.added_rules.update(self.iterate_changed_rules(items))


    def dict_added(self, items):
        if len(items) != len(set(items) & set(FILTER_LIST)):
            self.add_profile_test(self.product, self.profile)


    def dict_removed(self, items):
        if len(items) != len(set(items) & set(FILTER_LIST)):
            self.add_profile_test(self.product, self.profile)


    def type_changed(self, items):
        self.add_profile_test(self.product, self.profile)

    
    def analyse_changes(self):
        # Load previous and new profile
        yaml_before = yaml.safe_load(self.content_before)
        yaml_after = yaml.safe_load(self.content_after)

        # Find differencies in two dictionaries and ignore order
        deep_diff = DeepDiff(yaml_before, yaml_after, ignore_order=True)

        for change_type, change in deep_diff.items():
            if change_type == "dictionary_item_added":
                self.dict_added(change)
            elif change_type =="dictionary_item_removed":
                self.dict_removed(change)
            elif change_type == "type_changes":
                self.type_changed(change)
            elif change_type == "values_changed": # Check what value got changed
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
            self.diff_struct.added_rules = rules 
        except KeyError:
            logger.warning("New profile doesn't contain any rule.")
        self.add_profile_test(self.product, self.profile)


    def process_analysis(self):
        logger.info("Analyzing profile file " + self.filepath)

        if self.is_added():
            self.new_profile_added()
            return
        elif self.is_removed():
            return

        self.analyse_changes()
        self.diff_struct.find_dependent_profiles(self.diff_struct.absolute_path,
                                                 self.profile)

        logger.info("Added rules to profile: %s", " ".join(self.diff_struct.added_rules))
        logger.info("Removed rules to profile: %s", " ".join(self.diff_struct.removed_rules))
