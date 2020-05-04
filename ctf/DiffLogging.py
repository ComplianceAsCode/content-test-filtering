import logging

logger = logging.getLogger("content-test-filtering.logging")

RAW_FORMAT = {
    "findings": "Changes identified:",
    "type_prefix": "  ",
    "list_prefix": "    ",
    "tests": "Recommended tests to execute:",
    "end_line": "\n"
}

MARKDOWN_FORMAT = {
    "findings": "**Changes identified:**",
    "type_prefix": "",
    "list_prefix": " ",
    "tests": "**Recommended tests to execute:**",
    "end_line": "\n"
}


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

    def print_all_logs(self, tests=None, format="raw"):
        if format == "raw":
            format_style = RAW_FORMAT
        elif format == "markdown":
            format_style = MARKDOWN_FORMAT

        if self.rules or self.profiles or self.macros or self.functionality:
            print(format_style["findings"], end=format_style["end_line"])

        for rule in self.rules:
            print("%sRule %s:" % (format_style["type_prefix"], rule), end=format_style["end_line"])
            for msg in self.rules[rule]:
                print("%s%s" % (format_style["list_prefix"], msg), end=format_style["end_line"])
        for profile in self.profiles:
            print("%sProfile %s:" % (format_style["type_prefix"], profile), end=format_style["end_line"])
            for msg in self.profiles[profile]:
                print("%s%s" % (format_style["list_prefix"], msg), end=format_style["end_line"])
        for macro in self.macros:
            print("%sMacro %s:" % (format_style["type_prefix"], macro), end=format_style["end_line"])
            for msg in self.macros[macro]:
                print("%s%s" % (format_style["list_prefix"], msg), end=format_style["end_line"])
        if self.functionality:
            print("%sOthers:" % format_style["type_prefix"], end=format_style["end_line"])
            for msg in self.functionality:
                print("%s%s" % (format_style["list_prefix"], msg), end=format_style["end_line"])

        if tests:
            print(end=format_style["end_line"])
            print(format_style["tests"], end=format_style["end_line"])
            for test in tests:
                print("%s%s" % (format_style["list_prefix"], test), end=format_style["end_line"])

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
