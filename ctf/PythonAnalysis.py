import ast
import itertools
import logging
from ctf.AbstractAnalysis import AbstractAnalysis
from ctf.PythonDiff import PythonDiffStruct

logger = logging.getLogger("content-test-filtering.diff_analysis")


class PythonAnalysis(AbstractAnalysis):
    def __init__(self, file_record):
        super().__init__(file_record)
        self.diff_struct = PythonDiffStruct(self.absolute_path)

    # Source: https://stackoverflow.com/a/19598419/11067001 by Yorik.sar
    def compare_ast(self, node1, node2):
        if type(node1) is not type(node2):
            return False
        if isinstance(node1, ast.AST):
            for k, v in vars(node1).items():
                if k in ('lineno', 'end_lineno', 'col_offset', 'end_col_offset', 'ctx'):
                    continue
                if not self.compare_ast(v, getattr(node2, k)):
                    return False
            return True
        elif isinstance(node1, list):
            return all(self.compare_ast(n1, n2) for n1, n2 in zip(node1, node2))
        else:
            return node1 == node2

        
    def process_analysis(self):
        logger.info("Analyzing python file " + self.filepath)

        if self.file_flag == 'A':
            pass
        elif self.file_flag == 'D':
            pass

        ast_before = ast.parse(self.content_before)
        ast_after = ast.parse(self.content_after)
        if not self.compare_ast(ast_before, ast_after):
            self.diff_struct.changed = True

        return self.diff_struct
