import logging

logger = logging.getLogger("content-test-filtering.ContentTests")


class PythonTest:
    def __init__(self, path):
        self.absolute_path = path


class ProductTest:
    def __init__(self, path, product):
        self.absolute_path = path
        self.product = product


class RulesTest:
    def __init__(self, path, profile, product, rules_list, remediation="bash"):
        self.absolute_path = path
        self.profile = profile
        self.product = product
        self.rules_list = rules_list
        self.remediation = remediation


class ProfileTest:
    def __init__(self, path, profile, product):
        self.absolute_path = path
        self.profile = profile
        self.product = product


class ContentTests:
    def __init__(self):
        self.product_build = []
        self.rules = []
        self.profiles = []

    def add_product_build(self, path, product):
        product_build = ProductTest(path, product)
        self.product_build.append(product_build)

    def add_profile_test(self, path, profile, product):
        profile_test = ProfileTest(path, profile, product)
        self.profiles.append(profile_test)

    def add_rules_test(self, path, profile, product, rules_list, remediation="bash"):
        rules_test = RulesTest(path, profile, product, rules_list, remediation)
        self.rules.append(rules_test)

    def add_python_test(self, path):
        print("python tests...")

    def get_product(self):
        for profile in self.profiles:
            yield profile.product