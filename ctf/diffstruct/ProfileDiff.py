import os
import re
import yaml
from ctf.diffstruct.AbstractDiffStruct import AbstractDiffStruct
from ctf.constants import FileType


class ProfileDiffStruct(AbstractDiffStruct):
    def __init__(self, absolute_path):
        super().__init__(absolute_path)
        self.file_type = FileType.YAML
        self.product = None
        self.profile = None
        self.base_profile = None
        self.added_rules = set()
        self.removed_rules = set()
        self.extended_profiles = []


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
            self.extended_profiles.append(profile_name)
            self.find_dependent_profiles(f, profile_name)
