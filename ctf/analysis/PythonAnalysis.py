import ast
import logging
from ctf.analysis.AbstractAnalysis import AbstractAnalysis
from ctf.constants import FileType

logger = logging.getLogger("content-test-filtering.diff_analysis")


class PythonAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct.file_type = FileType.PYTHON

    @staticmethod
    def can_analyse(filepath):
        if filepath.endswith(".py"):
            return True
        return False

    def are_ast_same(self, node1, node2):
        if type(node1) is not type(node2):
            return False
        if isinstance(node1, ast.AST):
            for k, v in vars(node1).items():
                if k in ('lineno', 'end_lineno', 'col_offset',
                         'end_col_offset', 'ctx'):
                    continue
                if not self.are_ast_same(v, getattr(node2, k)):
                    return False
            return True
        elif isinstance(node1, list):
            return all(self.are_ast_same(n1, n2) for n1, n2 in zip(node1, node2))
        else:
            return node1 == node2

    def process_analysis(self):
        logger.debug("Analyzing python file %s", self.filepath)

        if self.is_added():
            self.diff_struct.add_functionality_test(msg="Python file %s is newly added."
                                                    % self.filepath)
            return self.diff_struct
        elif self.is_removed():
            self.diff_struct.add_functionality_test(msg="Python file %s was deleted."
                                                    % self.filepath)
            return self.diff_struct

        ast_before = ast.parse(self.content_before)
        ast_after = ast.parse(self.content_after)
        if not self.are_ast_same(ast_before, ast_after):
            self.diff_struct.add_functionality_test(
                msg="Python abstract syntax tree change found in %s." % self.filepath)

        return self.diff_struct
