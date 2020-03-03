import os
import re
import sys
import logging
from itertools import chain
from deepdiff import DeepDiff
from xmldiff import main, formatting, actions
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.OVALDiff import OVALDiffStruct
import xml.etree.ElementTree as ET
from io import StringIO

logger = logging.getLogger("content-test-filtering.diff_analysis")


class OVALAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = OVALDiffStruct(self.absolute_path)
        self.rule_name = re.match(r".+/(\w+)/oval/\w+\.xml$", self.absolute_path).group(1)
        self.tree_before = None
        self.tree_after = None

    def is_templated(self, content):
        no_templates = re.sub(r"^\s*{{{(.|\n)+?}}}\s*$", "", content, flags=re.MULTILINE)
        no_comments = re.sub(r"^\s*<\!--(.|\n)+?-->\s*$", "", no_templates, flags=re.MULTILINE)
        lines = no_comments.split("\n")
        lines = [line for line in lines if not re.match(r"\s*(\s*|#.*)$", line)]
        templated = False if lines else True
        return templated

    def add_product_test(self):
        # TODO solve if the rule is not present in any profile
        products = self.get_rule_products(self.diff_struct.rule)
        if products:
            self.diff_struct.product = products[0]

    def find_affected_rules(self):
        self.diff_struct.rule = self.rule_name
        self.diff_struct.affected_rules.add(self.rule_name)
        self.add_product_test()
        all_ids = {self.diff_struct.rule}

        for node_id in chain(self.tree_before.findall(".//*[@id]"), self.tree_after.findall(".//*[@id]")):
            all_ids.add(node_id.attrib["id"])

        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if d not in ["build", "build_new", "build_old"]]
            for file in files:
                if not file.endswith("xml"):
                    continue
                filepath = root + "/" + file
                with open(filepath) as f:
                    f.seek(0)
                    file_content = f.read()
                    for one_id in all_ids:
                        if 'definition_ref="' + one_id in file_content:
                            rule_name = re.search(r"/((?:\w|-)+)/oval", filepath)
                            self.diff_struct.affected_rules.add(rule_name.group(1))
        
    def add_rule_test(self):
        if not self.diff_struct.affected_rules:
            self.find_affected_rules()

    def load_diff(self):
        diff = DeepDiff(self.content_before, self.content_after)
        diff = diff["values_changed"]["root"]["diff"]

        return diff

    def get_unidiff_changes(self, diff):
        no_header = re.sub(r"^(\+\+\+\s*|---\s*|@@.+@@)\n", "", diff, flags=re.MULTILINE)
        changes = re.sub(r"^[^+-].*\n?", "", no_header, flags=re.MULTILINE)
        changes = re.sub(r"^\s*\n", "", changes, flags=re.MULTILINE)
        changes = [line for line in changes.split("\n") if line.strip() != ""]
        return changes

    def insert_node_change(self, change):
        if "/metadata/" in change.target:
            return
        else:
            self.add_rule_test()

    def delete_node_change(self, change):
        if "/metadata/" in change.node:
            return
        else:
            self.add_rule_test()

    def move_node_change(self, change):
        # Node moved within same node should not change behavior of the rule
        if ("/metadata/" in change.node and "/metadata/" in change.target) or\
           ("/criteria/" in change.node and "/criteria/" in change.target) or\
           ("textfilecontent54_test/" in change.node and "textfilecontent54_test/" in change.target) or\
           ("textfilecontent54_object/" in change.node and "textfilecontent54_object/" in change.target) or\
           ("textfilecontent54_state/" in change.node and "textfilecontent54_state/" in change.target):
            return
        else:
            self.add_rule_test()
        
    def delete_attr_change(self, change):
        if change.name == "comment" or change.name == "version":
            return
        else:
            self.add_rule_test()

    def rename_attr_change(self, change):
        if change.oldname == "comment" or change.oldname == "version":
            # Probably should perform product build for sanity (doesn't need to be tested)
            return
        else:
            self.add_rule_test()

    def update_attr_change(self, change):
        if change.name == "comment" or change.name == "version":
            return
        else:
            self.add_rule_test()

    def update_text_change(self, change):
        if "/title" in change.node or "/description" in change.node or "platform" in change.node:
            return
        else:
            self.add_rule_test() 


    def analyse_oval_change(self, change):
        if isinstance(change, actions.InsertNode):
            self.insert_node_change(change)
        elif isinstance(change, actions.DeleteNode):
            self.delete_node_change(change)
        elif isinstance(change, actions.MoveNode):
            self.move_node_change(change)
        # New atribute doesn't need to be tested. If it is a new attribute
        # in a new node -> InsertNode test will be performed
        elif isinstance(change, actions.InsertAttrib):
            pass
        elif isinstance(change, actions.DeleteAttrib):
            self.delete_attr_change(change)
        elif isinstance(change, actions.RenameAttrib):
            self.rename_attr_change
        elif isinstance(change, actions.UpdateAttrib):
            self.update_attr_change(change)
        elif isinstance(change, actions.UpdateTextIn):
            self.update_text_change(change)
        # Looks like a new text after node (NOT in node) -> must be tested everytime
        elif isinstance(change, actions.UpdateTextAfter):
            self.add_rule_test()
        # No analyse needed if it's a comment
        elif isinstance(change, actions.InsertComment):
            pass

    def analyse_template(self):
        diff = self.load_diff()
        changes = self.get_unidiff_changes(diff)

        for line in changes:
            if re.match(r"^(\+|-)\s*$", line):
                continue
            if re.match(r"(\+|-)\s*#.*$", line):
                continue
            self.add_rule_test()

    def analyse_oval(self):
        sys.path.insert(1, self.repository_path)
        import ssg.constants, ssg.build_ovals, ssg.xml
        header_without_ns = re.sub(r'\sxmlns="[^"]+"', '', ssg.constants.oval_header, count=1)
        wrapped_oval_before = (header_without_ns +
                              self.content_before +
                              ssg.constants.oval_footer)
        wrapped_oval_after = (header_without_ns +
                              self.content_after +
                              ssg.constants.oval_footer)
        self.tree_before = ET.fromstring(wrapped_oval_before)
        self.tree_after = ET.fromstring(wrapped_oval_after)

        changes = main.diff_texts(wrapped_oval_before, wrapped_oval_after)

        for change in changes:
            self.analyse_oval_change(change)


    def process_analysis(self):
        logger.info("Analyzing OVAL file " + self.filepath)

        was_templated = self.is_templated(self.content_before)
        is_templated = self.is_templated(self.content_after)

        if was_templated and is_templated:
            self.analyse_template()
        elif any([was_templated, is_templated]):
            self.add_rule_test()
            self.add_product_test()
        else:
            self.analyse_oval()

