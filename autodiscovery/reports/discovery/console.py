from autodiscovery.reports.discovery.base import AbstractDiscoveryReport
from autodiscovery.reports.console import AbstractConsoleReport


class ConsoleReport(AbstractConsoleReport, AbstractDiscoveryReport):
    @property
    def _header_column_width_map(self):
        """

        :return:
        """
        return {
            self.COMMENT_HEADER: 40,
            self.DESCRIPTION_HEADER: 60
        }
