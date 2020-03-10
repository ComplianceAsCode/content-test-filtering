import re
import os
import logging
import codecs
import importlib
import sys
from io import StringIO
from deepdiff import DeepDiff
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.diffstruct.JinjaDiff import JinjaDiffStruct
#from ctf.diff_analysis import analyse_file
import subprocess


logger = logging.getLogger("content-test-filtering.diff_analysis")


def get_suffix(filetype):
    if filetype == "ANACONDA":
        suffix = ".anaconda"
    elif filetype == "ANSIBLE":
        suffix = ".yml"
    elif filetype == "BASH":
        suffix = ".sh"
    elif filetype == "OVAL":
        suffix = ".xml"
    elif filetype == "PUPPET":
        suffix = ".pp"
    else:
        raise TypeError
    return suffix

def find_where_used(macro_name, filepath):
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

class JinjaMacroChange:
    # TODO chance repository_path as global variable
    def __init__(self, name, repository_path):
        self.name = name
        self.higher_macros = []
        self.in_rules = set()
        self.in_templates = set() # TODO - vyplnit + pokud pujde o template, pak poresit
        self.repository_path = repository_path
        self.find_usages()

    @staticmethod
    def is_valid(filepath):
        if filepath.endswith(".jinja"):
            return True
        return False

    def find_usages(self):
        for root, _, files in os.walk(self.repository_path):
            for file in files:
                filepath = root + "/" + file
                if filepath.endswith(".pyc") or filepath.endswith(".cache"):
                    continue
                # The folder may contain any unexpected files - TODO: investigate which (prob. skip them)
                with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(0)
                    if self.name in f.read():
                        # pridat parsovani template -> pokud je v template
                        # podle nazvu najdu rule.yml, ktere je pouzivaji
                        if filepath.endswith(".jinja"):
                            higher_macros = find_where_used(self.name, filepath)
                            for macro in higher_macros:
                                self.higher_macros.append(JinjaMacroChange(macro, self.repository_path))
                        else:
                            self.parse_rule_name(filepath)

    def parse_rule_name(self, filepath):
        name = re.search(r"/(\w+)/(?:bash/|ansible/|oval/|rule\.yml)", filepath)
        if name:
            self.in_rules.add(filepath)
            return

        name = re.search(r"\/template_\w+?_(\w+)$", filepath)
        if name:
            self.in_templates.add(filepath)

    
    def update_all_usages(self):
        for higher_macro in self.higher_macros:
            usages = higher_macro.update_all_usages()
            self.in_rules.update(usages)
        return self.in_rules


def mock_record(filepath, old_content, new_content, repo):
    record = {
        "flag": "M",
        "file_path": filepath,
        "repository_path": repo,
        "file_before": old_content,
        "file_after": new_content
    }

    return record


class JinjaAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = JinjaDiffStruct(self.absolute_path)
        self.changed_macros = []

    def analyse_changed_macros(self):
        for macro in self.changed_macros:
            macro.get_all_usages

    def analyse_macros(self):
        sys.path.insert(1, self.repository_path)
        import ssg.jinja
        
        default_macros = ssg.jinja.load_macros()
        updated_macros = ssg.jinja.load_macros()

        template_before = ssg.jinja._get_jinja_environment(default_macros).from_string(self.content_before)
        symbols = template_before.make_module(default_macros).__dict__
        # default_macros will contain old macros
        #ssg.jinja.update_substitutions_dict(previous_macros, default_macros)
        #template_after = ssg.jinja._get_jinja_environment(updated_macros).from_string(self.content_after)
        #symbols = template_after.make_module(updated_macros).__dict__
        #for name, symbol in symbols.items():
        #    updated_macros[name] = symbol
        # new_macros will contain changed macros
        #ssg.jinja.update_substitutions_dict(new_macros, updated_macros)

        for macro in self.changed_macros:
            del default_macros[macro.name]
            for name, symbol in symbols.items():
                default_macros[name] = symbol
            for rule in macro.in_rules:
                old_processed = ssg.jinja.process_file(rule, default_macros)
                new_processed = ssg.jinja.process_file(rule, updated_macros)
                file_record = mock_record(rule, old_processed, new_processed, self.repository_path)
                diff_struct = analyse_file(file_record)
                self.diff_struct.affected_files_diffs.append(diff_struct)
            for template in macro.in_templates:
                self.analyse_template(template)

    def analyse_template(self, template):
        match = re.search(r"\/template_(\w+?)_(\w+)$", template)
        file_type = match.group(1)
        macro_name = match.group(2)
        in_rules = []
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if d not in ["build", "build_new", "build_old", "docs", "utils", "ssg", ".git"]]
            for file in files:
                filepath = root + "/" + file
                if filepath.endswith(".pyc") or filepath.endswith(".cache"):
                    continue
                # The folder may contain any unexpected files - TODO: investigate which (prob. skip them)
                with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(0)
                    if macro_name in f.read():
                        rule_name = re.search(r".+\/(\w+)\/\w+\.\w+$", filepath).group(1)
                        rule_name = rule_name + get_suffix(file_type)
                        in_rules.append(rule_name)


        if not in_rules:
            return

        for root, dirs, files in os.walk(self.repository_path+"/build_new") :
            for file in files:
                if file in in_rules:
                    filepath = root + "/" + file    
                    with open(filepath) as f:
                        new_processed = f.read()
                    with open(filepath.replace("/build_new/", "/build_old/")) as f:
                        old_processed = f.read()
                    file_record = mock_record(filepath, old_processed, new_processed, self.repository_path)
                    diff_struct = analyse_file(file_record)
                    self.diff_struct.affected_files_diffs.append(diff_struct)


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
            m = re.match(r"^\+([^\+]*)$", line)
            if m:
                change["changed_lines"].append(m.group(1))
        return change 


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
        for macro in all_macros:
            # Find only macros with our markers
            if not re.search("(>|<){5}", macro):
                continue
            macro = macro.replace(">>>>>", "")
            macro = macro.replace("<<<<<", "")
            # Find macro name
            changed_macro = re.search(r"(?:\s|-)macro(?:\s|\n)+([^(]+)", macro)
            macro_name = changed_macro.group(1)
            macro_class = JinjaMacroChange(macro_name, self.repository_path)
            self.changed_macros.append(macro_class)

    def process_analysis(self):
        logger.info("Analyzing Jinja macro file " + self.filepath)
        diff = self.load_diff()
        changes = self.analyse_jinja_diff(diff)
        marked_changes = self.mark_changes_in_content(changes, self.content_after)
        all_macros = re.findall(r"{{%(?:\s|-|\n|>|<)+?macro(?:\s|\n|<|>)(?:.|\n)+?endmacro(?:\s|-|\n|>|<)+?%}}",
                                marked_changes)
        changed_macros = self.get_changed_macros(all_macros)


        
        self.content_after = self.content_after.replace(">>>>>", "")
        self.content_after = self.content_after.replace("<<<<<", "")
        for macro in self.changed_macros:
            macro.update_all_usages()

        self.analyse_macros()
