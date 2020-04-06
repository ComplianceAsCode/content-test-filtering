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

    def print_all_logs(self):
        for rule in self.rules:
            logger.info("Rule %s:", rule)
            for msg in self.rules[rule]:
                logger.info("    %s", msg)
        for profile in self.profiles:
            logger.info("Profile %s:", profile)
            for msg in self.profiles[profile]:
                logger.info("    %s", msg)
        for macro in self.macros:
            logger.info("Macro %s:", macro)
            for msg in self.macros[macro]:
                logger.info("    %s", msg)
        if self.functionality:
            logger.info("Others:")
            for msg in self.functionality:
                logger.info("    %s", msg)

    def add_rule_log(self, rule, msgs):
        for msg in msgs:
            if rule in self.rules:
                self.rules[rule].add(msg)
            else:
                self.rules[rule] = set([msg])

    def add_profile_log(self, profile, msgs):
        for msg in msgs:
            if profile in self.profiles:
                self.profiles[profile].add(msg)
            else:
                self.profiles[profile] = set([msg])

    def add_macro_log(self, macro, msgs):
        for msg in msgs:
            if macro in self.macros:
                self.macros[macro].add(msg)
            else:
                self.macros[macro] = set([msg])

    def add_functionality_log(self, msg):
        self.functionality.append(msg)
