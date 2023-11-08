import inspect
import pkgutil
import logging
from os import path

logger = logging.getLogger("content-test-filtering.diff_analysis")


class UnknownAnalysisFileType(Exception):
    def __init__(self, filepath=None):
        super().__init__(filepath)
        self.message = filepath if filepath else None

    def __str__(self):
        if self.message:
            message = "Unknown type of file %s" % self.message
        else:
            message = "Unknown file type for analysis"
        return message


def get_analyse_classes(modules):
    for module in modules:
        classes = inspect.getmembers(module, predicate=inspect.isclass)
        for _, class_obj in classes:
            methods = inspect.getmembers(class_obj, predicate=inspect.isfunction)
            for method_name, _ in methods:
                if method_name == "can_analyse":
                    yield class_obj


def analyse_file(file_record):
    file_analyzer = None
    analysis_modules = []

    # Load all modules from ctf/analysis folder
    for importer, package_name, _ in pkgutil.iter_modules([path.dirname(__file__)
                                                           + "/analysis"]):
        full_package_name = "%s.%s" % ("ctf.analysis", package_name)
        spec = importer.find_spec(full_package_name)
        module = spec.loader.load_module()
        analysis_modules.append(module)

    # Get all classes with "is_valid" method
    for analyse_class in get_analyse_classes(analysis_modules):
        if analyse_class.can_analyse(file_record["filepath"]):
            file_analyzer = analyse_class(file_record)
            break

    # Not found any valid class for file
    if not file_analyzer:
        raise UnknownAnalysisFileType(file_record["filepath"])

    return file_analyzer.process_analysis()
