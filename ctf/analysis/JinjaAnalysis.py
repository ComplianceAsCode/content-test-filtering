import re
import logging
import codecs
import importlib
import sys
from deepdiff import DeepDiff
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.diffstruct.JinjaDiff import JinjaDiffStruct
from ctf.utils import get_repository_files, get_suffix
from ctf.diff import git_wrapper

logger = logging.getLogger("content-test-filtering.diff_analysis")



class JinjaMacroChange:
    def __init__(self, name):
        self.name = name
        self.higher_macros = []
        self.in_rules = set()
        self.in_templates = set() # TODO - vyplnit + pokud pujde o template, pak poresit
        self.find_usages()


    def find_where_macro_used(self, macro_name, filepath):
        usages = []
        with open(filepath) as f:
            f.seek(0)
            content = f.read()
            matches = re.findall(r"{{%(?:\s|-|\n)+?macro(?:\s|\n)(?:.|\n)+?endmacro(?:\s|-|\n)+?%}}", content)

            for match in matches:
                higher_macro = re.search(r"(?:\s|-)macro(?:\s|\n)+([^(]+)\((?:.|\n)+" + macro_name, match)
                if higher_macro:
                    usages.append(higher_macro.group(1))
            return usages


    def find_usages(self):
        for content_file in get_repository_files():
            # The folder may contain any unexpected files - TODO: investigate which (prob. skip them)
            with codecs.open(content_file, "r",
                             encoding="utf-8", errors="ignore") as f:
                f.seek(0)
                if not self.name in f.read(): # Macro is not used in the file -> continue
                    continue
            if content_file.endswith(".jinja"):
                higher_macros = self.find_where_macro_used(self.name, content_file)
                for macro in higher_macros:
                    higher_macro_class = JinjaMacroChange(macro)
                    self.higher_macros.append(higher_macro_class)
            else:
                self.parse_macro_usage(content_file)
        self.update_all_usages()


    def parse_macro_usage(self, filepath):
        if re.search(r"/(\w+)/(?:bash/|ansible/|oval/|rule\.yml)", filepath):
            self.in_rules.add(filepath)
        elif re.search(r"\/template_\w+?_((?:\w|_|-)+)$", filepath):
            self.in_templates.add(filepath)
        else:
            raise TypeError


    def update_all_usages(self):
        # Find all usages in higher macros and update with usages lower macros
        for higher_macro in self.higher_macros:
            usages = higher_macro.update_all_usages()
            self.in_rules.update(usages)
        return self.in_rules


def mock_record(filepath, old_content, new_content):
    record = {
        "flag": "M",
        "filepath": filepath,
        "file_before": old_content,
        "file_after": new_content
    }

    return record


class JinjaAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = JinjaDiffStruct(self.filepath)


    @staticmethod
    def is_valid(filepath):
        if filepath.endswith(".jinja"):
            return True
        return False


    def get_ssg_jinja_module(self):
        git_dif = importlib.import_module("ctf.diff")
        spec = importlib.util.spec_from_file_location("ssg",
                                                      git_dif.git_wrapper.repo_path
                                                      + "/ssg/__init__.py")
        sys.modules["ssg"] = importlib.util.module_from_spec(spec)
        ssg_jinja = importlib.import_module("ssg.jinja", package="ssg")
        return ssg_jinja


    def analyse_macros_in_rules(self, macros):
        ssg_jinja = self.get_ssg_jinja_module()
        # Load macros from current project state
        default_macros = ssg_jinja.load_macros()
        updated_macros = ssg_jinja.load_macros()
        # Get symbols from old project state
        template_before = ssg_jinja._get_jinja_environment(default_macros).from_string(
            self.content_before)
        symbols = template_before.make_module(default_macros).__dict__

        for macro in macros:
            # Remove new macro and replace it with old macro
            del default_macros[macro.name]
            for name, symbol in symbols.items():
                default_macros[name] = symbol
            # Build each rule with old and new macro, and add it diff_struct for analysis
            for rule in macro.in_rules:
                old_processed = ssg_jinja.process_file(rule, default_macros)
                new_processed = ssg_jinja.process_file(rule, updated_macros)
                file_record = mock_record(rule, old_processed, new_processed)
                self.diff_struct.affected_files.append(file_record)


    def analyse_macros_in_templates(self, macros):
        nonempty_macros = [macro for macro in macros if macro.in_templates]
        if not nonempty_macros:
            return

        #git_wrapper.build_project("/build_new/", "/build_old/")
        for macro in macros:
            for template in macro.in_templates:
                self.analyse_template(template)


    def analyse_macros(self, macros):
        self.analyse_macros_in_rules(macros)
        self.analyse_macros_in_templates(macros)


    def find_template_usage(self, filepath):
        match = re.search(r"\/template_(\w+?)_((?:\w|_|-)+)$", filepath)
        file_type = match.group(1)
        macro_name = match.group(2)
        in_rules = []

        for content_file in get_repository_files():
            # The folder may contain any unexpected files - TODO: investigate which (prob. skip them)
            with codecs.open(content_file, 'r', encoding='utf-8',
                             errors='ignore') as f:
                f.seek(0)
                if macro_name in f.read():
                    rule_name = re.search(r".+\/(\w+)\/\w+\.\w+$", content_file).group(1)
                    rule_name = rule_name + get_suffix(file_type)
                    in_rules.append(rule_name)
        return in_rules


    def analyse_template(self, template):
        in_rules = self.find_template_usage(template)
        if not in_rules:
            return

        git_wrapper.build_project("/build_old/", "/build_new/")
        # Get new and old builded template and compare them
        for build_file in get_repository_files("/build_new"):
            if not build_file.split("/")[-1] in in_rules:
                continue
            with open(build_file) as f:
                new_processed = f.read()
            with open(build_file.replace("/build_new/", "/build_old/")) as f:
                old_processed = f.read()
            file_record = mock_record(build_file, old_processed, new_processed)
            self.diff_struct.affected_files.append(file_record)


    def load_diff(self):
        diff = DeepDiff(self.content_before, self.content_after)
        diff = diff["values_changed"]["root"]["diff"]
        return diff


    def analyse_jinja_diff(self, diff):
        changes = []
        for line in diff.split("\n"):
            m = re.match(r"@@\s-(.+)\s\+(.+)\s@@", line)
            if m:
                change = {"changed_lines": []}
                diff_lines = m.group(2).split(",")
                change["starting_line"] = int(diff_lines[0])
                if len(diff_lines) > 1:
                    change["number_of_lines"] = int(diff_lines[1])
                else:
                    change["number_of_lines"] = 1
                changes.append(change)
            m = re.match(r"^(?:\+|-)([^\+-]*)$", line)
            if m:
                change["changed_lines"].append(m.group(1))
        return changes


    def mark_changes_in_content(self, changes, content):
        changed_lines = []
        # Find lines in changed part of content (starting and number of
        # lines is known from unified diff)
        for i, line in enumerate(content.split("\n"), start=1): # unidiff starts at 1
            for change in changes:
                if i not in range(change["starting_line"],
                                  change["starting_line"]+change["number_of_lines"]):
                    continue
                for changed_line in change["changed_lines"]:
                    if changed_line == line:
                        changed_lines.append(i-1) # Indexing starts at 0
        content = content.split("\n")
        for i in changed_lines:
            content[i] = ">>>>>" + content[i] + "<<<<<"
        content = "\n".join(content)
        return content


    def get_changed_macros(self, all_macros):
        changed_macros = []
        for macro in all_macros:
            # Find only macros with our markers
            if not re.search("(>|<){5}", macro):
                continue
            macro = macro.replace(">>>>>", "").replace("<<<<<", "")
            # Find macro name
            macro_header = re.search(r"(?:\s|-)macro(?:\s|\n)+([^(]+)", macro)
            macro_name = macro_header.group(1)
            macro_class = JinjaMacroChange(macro_name)
            changed_macros.append(macro_class)
        return changed_macros


    def find_all_macros(self, input_string):
        all_macros = re.findall(r"{{%(?:\s|-|\n|>|<)+?macro(?:\s|\n|<|>)(?:.|\n)+?endmacro(?:\s|-|\n|>|<)+?%}}",
                                input_string)
        return all_macros


    def find_changed_macros(self, diff_output, content):
        marked_changes = self.mark_changes_in_content(diff_output, content)
        all_macros = self.find_all_macros(marked_changes)
        changed_macros = self.get_changed_macros(all_macros)
        return changed_macros


    def process_analysis(self):
        logger.info("Analyzing Jinja macro file " + self.filepath)
        diff = self.load_diff()
        changes = self.analyse_jinja_diff(diff)

        changed_old_macros = self.find_changed_macros(changes, self.content_before)
        changed_new_macros = self.find_changed_macros(changes, self.content_after)

        changed_macros = changed_new_macros if changed_new_macros else changed_old_macros

        self.analyse_macros(changed_macros)
