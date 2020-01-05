from autodiscovery.common.consts import ResourceModelsAttributes
from autodiscovery.exceptions import ReportableException
from autodiscovery.handlers.base import AbstractHandler


class PDUTypeHandler(AbstractHandler):
    def discover(self, entry, vendor, vendor_settings):
        """Discover device attributes.

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.PDUVendorDefinition vendor:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        :rtype: autodiscovery.reports.base.Entry
        """
        cli_creds = self._get_cli_credentials(
            vendor=vendor, vendor_settings=vendor_settings, device_ip=entry.ip
        )
        if cli_creds is None:
            entry.comment = "Unable to discover device user/password"
        else:
            entry.add_attribute(ResourceModelsAttributes.USER, entry.user)
            entry.add_attribute(ResourceModelsAttributes.PASSWORD, entry.password)

        return entry

    async def upload(self, entry, vendor, cs_session):
        """Upload discovered device on the CloudShell.

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.PDUVendorDefinition vendor:
        :param autodiscovery.common.async_cloudshell_api.AsyncCloudShellAPISession cs_session:
        :return:
        """
        resource_name = await self._upload_resource(
            cs_session=cs_session,
            entry=entry,
            resource_family=vendor.family_name,
            resource_model=vendor.model_name,
            driver_name=vendor.driver_name,
        )

        if not resource_name:
            raise ReportableException(f"Shell {vendor.driver_name} is not installed")
