import os
import re
import logging
from ctf.diff import git_wrapper
from ctf.utils import file_path_to_log

logger = logging.getLogger("content-test-filtering.diff")


class DiffStruct:
    def __init__(self, filepath):
        self.absolute_path = git_wrapper.repo_path + "/" + filepath
        # Remove duplicite slashes in filepath (e.g. from parameter)
        self.absolute_path = self.absolute_path.replace("//", "/")
        self.file_type = None
        self.changed_rules = {}  # {"product": {"rule_1", "rule_2"}, ...}
        self.changed_profiles = {}  # {"product": {"profile_1", "profile_2"}, ...}
        self.changed_products = set()
        self.funcionality_changed = False
        self.affected_files = []
        self.rules_logging = {}
        self.profiles_logging = {}
        self.products_logging = {}
        self.macros_logging = {}
        self.functionality_logging = set()

    def get_changed_rules_with_products(self):
        for product in self.changed_rules:
            for rule in self.changed_rules[product]:
                yield product, rule

    def get_changed_profiles_with_products(self):
        for product in self.changed_profiles:
            for profile in self.changed_profiles[product]:
                yield product, profile

    def find_rule_profiles(self, rule):
        product_folders = []

        # Walk through project folder and
        # find all folders with subfolder "profiles" (=product folder)
        for content_file in os.listdir(git_wrapper.repo_path):
            subfolder = git_wrapper.repo_path + "/" + content_file
            if not os.path.isdir(subfolder):
                continue

            for subfile in os.listdir(subfolder):
                if subfile == "profiles":
                    product_folders.append(subfolder)

        find_rule = re.compile(r"^\s*-\s*" + rule + r"\s*$")
        # Create list of all profiles that contain the rule
        for folder in product_folders:
            for profile in os.listdir(folder + "/profiles"):
                profile_file = folder + "/profiles/" + profile
                with open(profile_file) as f:
                    for line in f:
                        if find_rule.search(line):
                            yield profile_file

    def get_rule_profiles(self, rule):
        profiles = []
        # Parse from matched profiles profile names
        for profile_path in self.find_rule_profiles(rule):
            parse_file = re.match(r".+/(?:\w|-)+/profiles/((?:\w|-)+)\.profile",
                                  profile_path)
            profiles.append(parse_file.group(1))

        return profiles

    def get_rule_products(self, rule):
        products = []
        # Parse from matched profiles product names
        for profile_path in self.find_rule_profiles(rule):
            parse_file = re.match(r".+/((?:\w|-)+)/profiles/(?:\w|-)+\.profile",
                                  profile_path)
            products.append(parse_file.group(1))

        return products

    def add_changed_rule(self, rule_name, product_name=None, msg=""):
        self.add_rule_log(rule_name, msg)
        if not product_name:
            product_name = self.get_rule_products(rule_name)
            if product_name:
                product_name = product_name[0]
            else:
                msg = "The rule doesn't occur in any profile nor product."
                self.add_rule_log(rule_name, msg)
                return
        logger.debug("Rule %s is part of %s datastream.", rule_name, product_name)
        if product_name in self.changed_rules:
            self.changed_rules[product_name].add(rule_name)
        else:
            self.changed_rules[product_name] = {rule_name}

    def add_changed_profile(self, profile_name, product_name, msg=""):
        profile_product = "%s on %s" % (profile_name, product_name)
        self.add_profile_log(profile_product, msg)
        if product_name in self.changed_profiles:
            self.changed_profiles[product_name].add(profile_name)
        else:
            self.changed_profiles[product_name] = {profile_name}

    def add_changed_product_by_rule(self, rule_name, msg=""):
        product_name = self.get_rule_products(rule_name)
        if product_name:
            product_name = product_name[0]
        else:
            msg = "The rule doesn't occur in any profile nor product."
            self.add_rule_log(rule_name, msg)
            return
        logger.debug("Rule %s is part of %s datastream.", rule_name, product_name)
        self.changed_products.add(product_name)

    def add_functionality_test(self, msg=""):
        self.add_functionality_log(msg)
        self.funcionality_changed = True

    def add_rule_log(self, rule, msg):
        if rule in self.rules_logging:
            self.rules_logging[rule].add(msg)
        else:
            self.rules_logging[rule] = {msg}

    def add_profile_log(self, profile, msg):
        if profile in self.profiles_logging:
            self.profiles_logging[profile].add(msg)
        else:
            self.profiles_logging[profile] = {msg}

    def add_functionality_log(self, msg):
        if self.functionality_logging:
            self.functionality_logging.add(msg)
        else:
            self.functionality_logging = {msg}

    def add_macro_log(self, macro, msg):
        if macro in self.macros_logging:
            self.macros_logging[macro].add(msg)
        else:
            self.macros_logging[macro] = {msg}

    def add_macro_rule_log(self, macro, usage_list):
        for usage in usage_list:
            msg = file_path_to_log(usage)
            if macro in self.macros_logging:
                self.macros_logging[macro].add(msg)
            else:
                self.macros_logging[macro] = {msg}

    def add_macro_template_log(self, macro, msg):
        pass
