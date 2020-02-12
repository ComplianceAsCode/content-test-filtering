import re
import os
import fnmatch
from abc import ABC, abstractmethod
import jinja2
from ruamel.yaml import YAML


class AbstractAnalysis(ABC):
    def __init__(self, file_record):
        self.diff_struct = None
        self.repository_path = file_record["repository_path"]
        self.filepath = file_record["file_path"]
        self.file_flag = file_record["flag"]
        self.file_name = self.filepath.split("/")[-1]
        self.absolute_path = self.repository_path + "/" + self.filepath
        self.content_before = file_record["file_before"]
        self.content_after = file_record["file_after"]

    @abstractmethod
    def process_analysis(self):
        pass

    def analyse(self):
        self.process_analysis()
        return self.diff_struct

    def find_profiles(self, rule):
        profile_folders = []
        matched_profiles = []

        for content_file in os.listdir(self.repository_path):
            subfolder = self.repository_path + "/" + content_file
            if not os.path.isdir(subfolder):
                continue

            for subfile in os.listdir(subfolder):
                if subfile == "profiles":
                    profile_folders.append(subfolder)

        find_rule = re.compile(r"^\s*-\s*" + rule + r"\s*$")
        for folder in profile_folders:
            for profile in os.listdir(folder + "/profiles"):
                profile_file = folder + "/profiles/" + profile
                with open(profile_file) as f:
                    for line in f:
                        if find_rule.search(line):
                            matched_profiles.append(profile_file)
        
        return matched_profiles

    def get_rule_profiles(self, rule):
        matched_profiles = self.find_profiles(rule)
        profiles = []

        for filepath in matched_profiles:
            parse_file = re.match(r".+/(?:\w+)/profiles/(\w|-)+\.profile", filepath)
            profiles.append(parse_file.group(1))
        
        return profiles

    def get_rule_products(self, rule):
        matched_profiles = self.find_profiles(rule)
        products = []
        for filepath in matched_profiles:
            parse_file = re.match(r".+/(\w+)/profiles/(?:\w|-)+\.profile", filepath)
            products.append(parse_file.group(1))

        return products

    def connect_labels(self):
        product = "rhel8"
        yaml = YAML(typ="safe")
        template_loader = jinja2.FileSystemLoader(searchpath="./")
        template_env = jinja2.Environment(loader=template_loader)
        yaml_content = yaml.load(template_env.get_template("test_labels.yml").render(product=product))
        print(yaml_content["rule_ansible"])