import re
import logging
import os
from abc import ABCMeta, abstractmethod
from ctf.diff import git_wrapper
import jinja2
from ruamel.yaml import YAML

logger = logging.getLogger("content_test_filtering.diff_analysis")


class AbstractAnalysis(metaclass=ABCMeta):
    def __init__(self, file_record):
        self.diff_struct = None
        self.filepath = file_record["filepath"]
        self.file_flag = file_record["flag"]
        self.file_name = self.filepath.split("/")[-1]
        self.content_before = file_record["file_before"]
        self.content_after = file_record["file_after"]

    @abstractmethod
    def process_analysis(self):
        pass


    @staticmethod
    @abstractmethod
    def is_valid(filepath):
        return False


    def analyse(self):
        self.process_analysis()
        return self.diff_struct


    def is_added(self):
        if self.file_flag == "A":
            logger.info("File %s has been added." % self.filepath)
            return True
        return False


    def is_removed(self):
        if self.file_flag == "D":
            logger.info("File %s has been removed." % self.filepath)
            return True
        return False
        

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
        for profile_path in self.get_rule_profiles(rule):
            parse_file = re.match(r".+/(?:\w|-)+/profiles/((?:\w|-)+)\.profile", profile_path)
            profiles.append(parse_file.group(1))
        
        return profiles

    def get_rule_products(self, rule):
        products = []
        # Parse from matched profiles product names
        for profile_path in self.get_rule_profiles(rule):
            parse_file = re.match(r".+/((?:\w|-)+)/profiles/(?:\w|-)+\.profile", profile_path)
            products.append(parse_file.group(1))

        return products
