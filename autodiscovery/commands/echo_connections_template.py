class EchoConnectionsTemplateCommand(object):
    def __init__(self, report):
        """

        :param autodiscovery.reports.connections.ExcelReport report:
        """
        self.report = report

    def execute(self):
        """Execute echo report file command

        :return:
        """
        with self.report.add_entry(resource_name="-",
                                   source_port="DUT 1/Chassis 1/Module 1/Port 1",
                                   adjacent="-",
                                   target_port="DUT 2/Chassis 1/Module 1/Port 1",
                                   domain="Global",
                                   offline=True) as entry:

            entry.status = "Skipped"
            entry.comment = "Auto-generated ports connection example"

        self.report.generate()
