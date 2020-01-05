from cloudshell.api.cloudshell_api import (
    AttributeNameValue,
    ResourceAttributesUpdateRequest,
)
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.cli_sessions import SSHDiscoverySession, TelnetDiscoverySession
from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.exceptions import ReportableException


class AbstractHandler:
    def __init__(self, logger, autoload):
        """Init command.

        :param logging.Logger logger:
        :param bool autoload:
        """
        self.logger = logger
        self.autoload = autoload

    def discover(self, entry, vendor, vendor_settings):
        """Discover device attributes.

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.BaseVendorDefinition vendor:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        :rtype: autodiscovery.reports.base.Entry
        """
        raise NotImplementedError(
            f"Class {type(self)} must implement method 'discover'"
        )

    def upload(self, entry, vendor, cs_session):
        """Upload discovered device on the CloudShell.

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.BaseVendorDefinition vendor:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_session:
        :return:
        """
        raise NotImplementedError(f"Class {type(self)} must implement method 'upload'")

    def _get_cli_credentials(self, vendor, vendor_settings, device_ip):
        """Get CLI credentials.

        :param autodiscovery.models.VendorDefinition vendor:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        :param str device_ip:
        :return:
        """
        vendor_cli_creds = vendor_settings.get_creds_by_vendor(vendor)

        if vendor_cli_creds:
            for session in (
                SSHDiscoverySession(device_ip),
                TelnetDiscoverySession(device_ip),
            ):
                try:
                    valid_creds = session.check_credentials(
                        cli_credentials=vendor_cli_creds,
                        default_prompt=vendor.default_prompt,
                        enable_prompt=vendor.enable_prompt,
                        logger=self.logger,
                    )
                except Exception:
                    self.logger.warning(
                        f"{session.SESSION_TYPE} Credentials aren't valid "
                        f"for the device with IP {device_ip}",
                        exc_info=True,
                    )
                else:
                    vendor_cli_creds.update_valid_creds(valid_creds)
                    return valid_creds

    async def _add_resource_driver(self, cs_session, resource_name, driver_name):
        """Add appropriate driver to the created CloudShell resource.

        :param autodiscovery.common.async_cloudshell_api.AsyncCloudShellAPISession cs_session:
        :param str resource_name:
        :param str driver_name:
        :return:
        """
        try:
            await cs_session.UpdateResourceDriver(
                resourceFullPath=resource_name, driverName=driver_name
            )
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_DRIVER:
                self.logger.exception(f"Unable to locate driver {driver_name}")
                raise ReportableException(
                    f"Shell {driver_name} is not installed on the CloudShell"
                )
            raise

    async def _create_cs_resource(
        self,
        cs_session,
        resource_name,
        resource_family,
        resource_model,
        device_ip,
        folder_path,
    ):
        """Create Resource on CloudShell with appropriate attributes.

        :param autodiscovery.common.async_cloudshell_api.AsyncCloudShellAPISession cs_session:
        :param str resource_name:
        :param str resource_family:
        :param str resource_model:
        :param str device_ip:
        :param str folder_path:
        :return: name for the created Resource
        :rtype: str
        """
        try:
            await cs_session.CreateResource(
                resourceFamily=resource_family,
                resourceModel=resource_model,
                resourceName=resource_name,
                resourceAddress=device_ip,
                folderFullPath=folder_path,
            )
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.RESOURCE_ALREADY_EXISTS:
                resource_name = f"{resource_name}-1"
                await cs_session.CreateResource(
                    resourceFamily=resource_family,
                    resourceModel=resource_model,
                    resourceName=resource_name,
                    resourceAddress=device_ip,
                    folderFullPath=folder_path,
                )
            else:
                self.logger.exception(
                    f"Unable to locate Shell with Resource Family/Name: "
                    f"{resource_family}/{resource_model}"
                )
                raise

        return resource_name

    async def _upload_resource(
        self,
        cs_session,
        entry,
        resource_family,
        resource_model,
        driver_name,
        attribute_prefix="",
    ):
        """Upload resource to the CloudShell.

        :param autodiscovery.common.async_cloudshell_api.AsyncCloudShellAPISession cs_session:
        :param entry:
        :param resource_family:
        :param resource_model:
        :param driver_name:
        :param attribute_prefix:
        :return:
        """
        if entry.folder_path != "":
            # create folder before uploading resource. If folder
            # was already created it will return successful result
            await cs_session.CreateFolder(folderFullPath=entry.folder_path)

        try:
            resource_name = await self._create_cs_resource(
                cs_session=cs_session,
                resource_name=entry.device_name,
                resource_family=resource_family,
                resource_model=resource_model,
                device_ip=entry.ip,
                folder_path=entry.folder_path,
            )
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_FAMILY_OR_MODEL:
                return
            else:
                raise

        self.logger.info(f"Adding attributes to the resource {resource_name}")
        attributes = [
            AttributeNameValue(f"{attribute_prefix}{key}", value)
            for key, value in entry.attributes.items()
        ]

        await cs_session.SetAttributesValues(
            [ResourceAttributesUpdateRequest(resource_name, attributes)]
        )

        self.logger.info(f"Attaching driver to the resource {resource_name}")
        await self._add_resource_driver(
            cs_session=cs_session, resource_name=resource_name, driver_name=driver_name
        )

        if self.autoload:
            self.logger.info(f"Autoloading resource {resource_name}")
            await cs_session.AutoLoad(resource_name)

        return resource_name
