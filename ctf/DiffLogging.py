import logging

logger = logging.getLogger("content-test-filtering.logging")


class DiffLogging:
    def __init__(self):
        self.rules = {}
        self.profiles = {}
        self.products = {}
        self.macros = {}
        self.functionality = []

    def fill_logging(self, diff_struct):
        for rule in diff_struct.rules_logging:
            self.add_rule_log(rule, diff_struct.rules_logging[rule])
        for profile in diff_struct.profiles_logging:
            self.add_profile_log(profile, diff_struct.profiles_logging[profile])
        for macro in diff_struct.macros_logging:
            self.add_macro_log(macro, diff_struct.macros_logging[macro])
        for functionality in diff_struct.functionality_logging:
            self.add_functionality_log(functionality)

    def print_all_logs(self, tests=None):
        print("Findings:")
        for rule in self.rules:
            print("  Rule %s:" % rule)
            for msg in self.rules[rule]:
                print("    %s" % msg)
        for profile in self.profiles:
            print("  Profile %s:" % profile)
            for msg in self.profiles[profile]:
                print("    %s" % msg)
        for macro in self.macros:
            print("  Macro %s:" % macro)
            for msg in self.macros[macro]:
                print("    %s" % msg)
        if self.functionality:
            print("  Others:")
            for msg in self.functionality:
                print("    %s" % msg)

        if tests:
            print("Recommended tests to execute:")
            for test in tests:
                print("  %s" % test)

    def add_rule_log(self, rule, msgs):
        for msg in msgs:
            if rule in self.rules:
                self.rules[rule].add(msg)
            else:
                self.rules[rule] = {msg}

    def add_profile_log(self, profile, msgs):
        for msg in msgs:
            if profile in self.profiles:
                self.profiles[profile].add(msg)
            else:
                self.profiles[profile] = {msg}

    def add_macro_log(self, macro, msgs):
        for msg in msgs:
            if macro in self.macros:
                self.macros[macro].add(msg)
            else:
                self.macros[macro] = {msg}

    def add_functionality_log(self, msg):
        self.functionality.append(msg)
