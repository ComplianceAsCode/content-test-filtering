import re
import logging
import importlib
import xml.etree.ElementTree as ET
from itertools import chain
from deepdiff import DeepDiff
from xmldiff import main, actions
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.constants import FileType
from ctf.utils import get_repository_files


logger = logging.getLogger("content-test-filtering.diff_analysis")


class OVALAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct.file_type = FileType.OVAL
        self.rule_name = re.match(r".+/(\w+)/oval/\w+\.xml$",
                                  self.diff_struct.absolute_path).group(1)
        self.tree_before = None
        self.tree_after = None

    @staticmethod
    def can_analyse(filepath):
        if re.match(r".*/oval/\w+\.xml$", filepath):
            return True
        return False

    def is_templated(self, content):
        no_templates = re.sub(r"^\s*{{{(.|\n)+?}}}\s*$", "",
                              content, flags=re.MULTILINE)
        no_comments = re.sub(r"^\s*<\!--(.|\n)+?-->\s*$", "",
                             no_templates, flags=re.MULTILINE)
        lines = no_comments.split("\n")
        lines = [line for line in lines if not re.match(r"\s*(\s*|#.*)$", line)]
        templated = not lines
        return templated

    def find_affected_rules(self):
        all_ids = set()
        affected_rules = []

        for node_id in chain(self.tree_before.findall(".//*[@id]"),
                             self.tree_after.findall(".//*[@id]")):
            all_ids.add(node_id.attrib["id"])

        for content_file in get_repository_files():
            if not content_file.endswith(".xml"):
                continue
            with open(content_file) as f:
                f.seek(0)
                file_content = f.read()
                for one_id in all_ids:
                    if 'definition_ref="' + one_id not in file_content:
                        continue
                    rule_match = re.search(r"/((?:\w|-)+)/oval", content_file)
                    rule_name = rule_match.group(1)
                    logger.debug("%s rule affected by the change.", rule_name)
                    if rule_name not in affected_rules:
                        affected_rules.append(rule_name)
        return affected_rules

    def add_rule_test(self, msg):
        self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
        affected_rules = self.find_affected_rules()
        for affected_rule in affected_rules:
            self.diff_struct.add_changed_rule(affected_rule,
                                              msg="%s is affected by %s change" %
                                              (affected_rule, self.rule_name))

    def load_diff(self):
        diff = DeepDiff(self.content_before, self.content_after)
        diff = diff["values_changed"]["root"]["diff"]
        return diff

    def get_unidiff_changes(self, diff):
        # Remove header and parse added/removed lines
        no_header = re.sub(r"^(\+\+\+\s*|---\s*|@@.+@@)\n", "",
                           diff, flags=re.MULTILINE)
        changes = re.sub(r"^[^+-].*\n?", "", no_header, flags=re.MULTILINE)
        changes = re.sub(r"^\s*\n", "", changes, flags=re.MULTILINE)
        changes = [line for line in changes.split("\n") if line.strip() != ""]
        return changes

    def insert_node_change(self, change):
        if "/metadata/" not in change.target:
            self.add_rule_test("New node inserted to OVAL check")

    def delete_node_change(self, change):
        if "/metadata/" not in change.node:
            self.add_rule_test("Node deleted from OVAL check")

    def move_node_change(self, change):
        # Node moved within same node should not change behavior of the rule
        if ("/metadata/" in change.node and "/metadata/" in change.target) or\
           ("/criteria/" in change.node and "/criteria/" in change.target) or\
           ("textfilecontent54_test/" in change.node and
            "textfilecontent54_test/" in change.target) or\
           ("textfilecontent54_object/" in change.node and
            "textfilecontent54_object/" in change.target) or\
           ("textfilecontent54_state/" in change.node and
            "textfilecontent54_state/" in change.target):
            return
        else:
            self.add_rule_test("Node moved within OVAL check")

    def delete_attr_change(self, change):
        if change.name != "comment" and change.name != "version":
            self.add_rule_test("Deleted attribute from OVAL check")

    def rename_attr_change(self, change):
        if change.oldname != "comment" and change.oldname != "version":
            self.add_rule_test("Attribute renamed in OVAL check")
        # Probably should perform product build for sanity?

    def update_attr_change(self, change):
        if change.name != "comment" and change.name != "version":
            self.add_rule_test("Attribute value changed in OVAL check")

    def update_text_change(self, change):
        if ("/title" not in change.node and
            "/description" not in change.node and
            "platform" not in change.node):
            self.add_rule_test("Text changed in OVAL check")

    def analyse_oval_change(self, change):
        # TODO: Should it be analysed separately each change?
        if isinstance(change, actions.InsertNode):
            self.insert_node_change(change)
        elif isinstance(change, actions.DeleteNode):
            self.delete_node_change(change)
        elif isinstance(change, actions.MoveNode):
            self.move_node_change(change)
        elif isinstance(change, actions.DeleteAttrib):
            self.delete_attr_change(change)
        elif isinstance(change, actions.RenameAttrib):
            self.rename_attr_change(change)
        elif isinstance(change, actions.UpdateAttrib):
            self.update_attr_change(change)
        elif isinstance(change, actions.UpdateTextIn):
            self.update_text_change(change)
        # Looks like a new text after node (NOT in node) -> must be tested
        elif isinstance(change, actions.UpdateTextAfter):
            self.add_rule_test("Text added outsite tags in OVAL check" % self.filepath)
        # InsertAttrib and InsertComment changes are ignored

    def get_changes(self):
        diff = self.load_diff()
        changes = self.get_unidiff_changes(diff)
        return changes

    def analyse_template(self):
        changes = self.get_changes()

        for line in changes:
            if re.match(r"^(\+|-)\s*$", line):
                continue
            if re.match(r"^(\+|-)\s*#.*$", line):
                continue
            self.add_rule_test("Template usage changed in OVAL check")

    def get_ssg_constants_module(self):
        git_diff = importlib.import_module("ctf.diff")
        spec = importlib.util.spec_from_file_location("ssg.constants",
                                                      git_diff.git_wrapper.repo_path
                                                      + "/ssg/constants.py")
        ssg_const = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ssg_const)
        return ssg_const

    def create_valid_oval(self, oval_content, ssg_constants):
        # Remove empty namespace from XML (caused errors in ET processing)
        header_without_ns = re.sub(r'\sxmlns="[^"]+"', '',
                                   ssg_constants.oval_header, count=1)
        wrapped_oval = (header_without_ns +
                        oval_content +
                        ssg_constants.oval_footer)
        return wrapped_oval

    def analyse_oval(self):
        # Load constants for OVAL header and footer
        ssg_const = self.get_ssg_constants_module()
        # Wrap OVAL for valid XML file
        wrapped_oval_before = self.create_valid_oval(self.content_before,
                                                     ssg_const)
        wrapped_oval_after = self.create_valid_oval(self.content_after,
                                                    ssg_const)
        # TODO: This is temporary solution to parse partially templated XMLs
        wrapped_oval_before = re.sub(r"{{%(.|\n)+?%}}", "", wrapped_oval_before)
        wrapped_oval_after = re.sub(r"{{%(.|\n)+?%}}", "", wrapped_oval_after)
        # Create ElementTrees
        self.tree_before = ET.fromstring(wrapped_oval_before)
        self.tree_after = ET.fromstring(wrapped_oval_after)
        # Compare ElementTrees and analyse changes
        changes = main.diff_texts(wrapped_oval_before, wrapped_oval_after)
        for change in changes:
            self.analyse_oval_change(change)

    def process_analysis(self):
        logger.debug("Analyzing OVAL file %s", self.filepath)
        logger.debug("Rule name: %s", self.rule_name)

        if self.is_added():
            msg = "OVAL check is newly added"
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            # Don't search for rule references if newly added.
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
            return self.diff_struct
        elif self.is_removed():
            logger.info("OVAL check for %s was deleted. No test for it will be selected.",
                        self.rule_name)
            return self.diff_struct

        was_templated = self.is_templated(self.content_before)
        is_templated = self.is_templated(self.content_after)

        if was_templated and is_templated:
            self.analyse_template()
        elif any([was_templated, is_templated]):
            msg = "Templatization usage changed in %s" % self.filepath
            self.diff_struct.add_changed_product_by_rule(self.rule_name, msg=msg)
            self.diff_struct.add_changed_rule(self.rule_name, msg=msg)
        else:
            self.analyse_oval()

        return self.diff_struct
