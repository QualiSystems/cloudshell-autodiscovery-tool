from collections import OrderedDict

from autodiscovery.reports import get_report as base_get_report
from autodiscovery.reports import parse_report as base_parse_report
from autodiscovery.reports.discovery.console import ConsoleReport
from autodiscovery.reports.discovery.csv_report import CSVReport
from autodiscovery.reports.discovery.excel import ExcelReport

REPORTS = (CSVReport, ExcelReport, ConsoleReport)
REPORTS_MAP = OrderedDict(
    [(report_cls.FILE_EXTENSION, report_cls) for report_cls in REPORTS]
)
DEFAULT_REPORT_TYPE = CSVReport.FILE_EXTENSION
REPORT_TYPES = REPORTS_MAP.keys()
EDITABLE_REPORT_TYPES = [
    report_type
    for report_type in REPORT_TYPES
    if report_type != ConsoleReport.FILE_EXTENSION
]


def get_report(report_file, report_type=DEFAULT_REPORT_TYPE):
    """Get Report object for the given type.

    :param str report_file:
    :param str report_type:
    :rtype: autodiscovery.reports.base.AbstractReport
    """
    return base_get_report(
        report_file=report_file, report_type=report_type, reports_map=REPORTS_MAP
    )


def parse_report(report_file):
    """Parse report file and it's data to the Report object based on it's file extension.

    :param report_file:
    :rtype: autodiscovery.reports.base.AbstractParsableReport
    """
    return base_parse_report(report_file=report_file, reports=REPORTS)
