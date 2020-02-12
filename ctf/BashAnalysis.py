import re
import logging
import shlex
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.BashDiff import BashDiffStruct

logger = logging.getLogger("content-test-filtering.diff_analysis")


class BashAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = BashDiffStruct(self.absolute_path)
        self.rule_name = re.match(r".+/(\w+)/bash/\w+\.sh$", self.filepath).group(1)

    def is_templated(self, content):
        no_templates = re.sub(r"^\s*{{{(.|\n)+?}}}\s*$", "", content, flags=re.MULTILINE)
        lines = no_templates.split("\n")
        # Delete empty and commented lines
        lines = [line for line in lines if not re.match(r"^\s*(\s*|#.*)$", line)]
        # If no lines left - only important code was template -> templated
        templated = False if lines else True
        return templated

    def add_product_test(self):
        products = self.get_rule_products(self.rule_name)
        if products:
            self.diff_struct.product = products[0]

    def add_rule_test(self):
        products = self.get_rule_products(self.rule_name)
        if products:
            self.diff_struct.produts = products[0]
        self.diff_struct.rule = self.rule_name

    def analyse_template(self):
        diff = self.load_diff()
        changes = self.get_unidiff_changes(diff)

        # Check all changed lines
        for line in changes:
            # Added/removed empty line
            if re.match(r"^(\+|-)\s*$", line):
                continue
            # Important comment
            if re.match(r"^(\+|-)\s*#\s*(platform|reboot|strategy|complexity|disruption)\s*=\s*.*$", line):
                self.add_product_test()
                continue
            # Not important comment
            if re.match(r"^(\+|-)\s*#.*$", line):
                continue
            self.add_rule_test()

    def analyse_bash(self):
        x = shlex.shlex(self.content_before)
        print(x.get_token())
        print(x.get_token())
        print(x.get_token())
        print(x.get_token())

        return
        lines = self.content_before.split("\n")
        no_comments = [x for x in lines if not re.match(r"^\s*#.*", x)]
        no_empty = [x for x in no_comments if not re.match(r"^\s*$", x)]
        print(no_empty)
        for line in no_empty:
            print(line)
            ast_before = bashlex.parse(line)
            print(ast_before)
        ast_after = bashlex.parse(self.content_after)
        print(ast_after)
        pass

    def process_analysis(self):
        logger.info("Analyzing bash file " + self.filepath)
        
        if self.file_flag == 'A':
            logger.info("New bash remediation " + self.filepath)
            self.add_product_test()
            self.add_rule_test()
        elif self.file_flag == 'D':
            logger.info("Removed bash remediation file " + self.filepath)
            return

        was_templated = self.is_templated(self.content_before)
        is_templated = self.is_templated(self.content_after)

        if was_templated and is_templated:
            self.analyse_template()
        elif any([was_templated, is_templated]):
            self.add_product_test()
            self.add_rule_test()
        else:
            self.analyse_bash()