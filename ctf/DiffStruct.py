import os
import re
import logging
from collections import defaultdict
from ctf.diff import git_wrapper
from ctf.utils import file_path_to_log

logger = logging.getLogger("content-test-filtering.diff")


class DiffStruct:
    def __init__(self, filepath):
        self.absolute_path = git_wrapper.repo_path + "/" + filepath
        # Remove duplicite slashes in filepath (e.g. from parameter)
        self.absolute_path = self.absolute_path.replace("//", "/")
        self.file_type = None
        self.changed_rules = defaultdict(set)  # {"product": {"rule1", ...}, ...}
        self.changed_profiles = defaultdict(set)  # {"product": {"profile1", ...}}
        self.changed_products = set()
        self.funcionality_changed = False
        self.affected_files = []
        self.rules_logging = defaultdict(set)
        self.profiles_logging = defaultdict(set)
        self.products_logging = defaultdict(set)
        self.macros_logging = defaultdict(set)
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

        # We know that products are in products/ folder
        # We want all products' paths
        products_folder = git_wrapper.repo_path + "/" + "products"
        for product_name in os.listdir(products_folder):
            product_path = products_folder + "/" + product_name
            if not os.path.isdir(product_path):
                continue

            for subfile in os.listdir(product_path):
                if subfile == "profiles":
                    product_folders.append(product_path)
                    continue

        find_rule = re.compile(r"^\s*-\s*" + rule + r"\s*$")
        # Create list of all profiles that contain the rule
        for folder in product_folders:
            for profile in os.listdir(folder + "/profiles"):
                profile_file = folder + "/profiles/" + profile
                with open(profile_file) as f:
                    for line in f:
                        if find_rule.search(line):
                            yield profile_file

    def find_rule_controls(self, rule):
        controls = []
        find_rule = re.compile(r"^\s*-\s*" + rule + r"\s*$", re.MULTILINE)
        control_folder = git_wrapper.repo_path + "/" + "controls/"
        # Check all yaml files in controls/
        for control in os.listdir(control_folder):
            if not control.endswith(".yml"):
                continue
            control_path = control_folder + control
            with open(control_path) as f:
                control_content = f.read()
                # If controls in separate directory, merge them to one string
                controls_dir = re.search(r"controls_dir:\s*(\w+)", control_content)
                if controls_dir:
                    controls_dir = controls_dir.group(1)
                    for c in os.listdir(control_folder + controls_dir):
                        with open(control_folder + controls_dir + "/" + c) as cf:
                            control_content += cf.read()
            # Search for rule in control content
            if find_rule.search(control_content):
                yield control.rstrip(".yml")

    def find_control_products(self, control):
        products_folder = git_wrapper.repo_path + "/" + "products"
        find_control = re.compile(r"^\s*-\s*" + control + r":", re.MULTILINE)
        # Find dirs with profile files
        for dir_path, _, files in os.walk(products_folder):
            for file in files:
                if not file.endswith(".profile"):
                    continue
                # Search if desired control is used and if so, return product
                with open(dir_path + "/" + file) as f:
                    for line in f:
                        if find_control.search(line):
                            yield re.match(r".*/products/([^/]+)", dir_path).group(1)

    def get_rule_ruleyml(self, rule):
        # Find a directory with a rule name and check if it has rule.yml file
        for root, dirs, files in os.walk(git_wrapper.repo_path):
            if root.endswith("/" + rule) and "rule.yml" in files:
                ruleyml_path = root + "/rule.yml"
                logger.debug("rule.yml path - %s", ruleyml_path)
                return ruleyml_path

        logger.debug("rule.yml was not found for %s", rule)
        return None

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
        # Find in controls and from controls get product
        for control in self.find_rule_controls(rule):
            for product in self.find_control_products(control):
                products.append(product)

        products = sorted(products, key=lambda k: (k!="rhel8", k!="rhel7", k!="ocp4", k))
        return products

    def add_changed_rule(self, rule_name, product_name=None, msg=""):
        self.add_rule_log(rule_name, msg)
        if not product_name:
            product_name = self.get_rule_products(rule_name)
            if product_name:
                product_name = product_name[0]
                logger.debug("Rule %s is part of %s datastream.", rule_name, product_name)
            else:
                product_name = "rhel8"
                logger.debug("Rule %s is not part of any datastream. "
                             "Added default rhel8 value",  rule_name)
        self.changed_rules[product_name].add(rule_name)

    def add_changed_profile(self, profile_name, product_name, msg=""):
        profile_product = "%s on %s" % (profile_name, product_name)
        self.add_profile_log(profile_product, msg)
        self.changed_profiles[product_name].add(profile_name)

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
        self.rules_logging[rule].add(msg)

    def add_profile_log(self, profile, msg):
        self.profiles_logging[profile].add(msg)

    def add_functionality_log(self, msg):
        self.functionality_logging.add(msg)

    def add_macro_log(self, macro, msg):
        self.macros_logging[macro].add(msg)

    def add_macro_rule_log(self, macro, usage_list):
        for usage in usage_list:
            msg = file_path_to_log(usage)
            self.macros_logging[macro].add(msg)

    def add_macro_template_log(self, macro, msg):
        pass
