import logging

from nodestream.pipeline.extractors import Extractor

from ..akamai_utils.cps_client import AkamaiCPSClient


class AkamaiCPSExtractor(Extractor):
    def __init__(self, **akamai_client_kwargs) -> None:
        self.client = AkamaiCPSClient(**akamai_client_kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def extract_records(self):
        desired_fields = ["id", "productionSlots", "ra", "networkConfiguration", "csr"]
        try:
            enrollments = self.client.list_cps_enrollments()
        except Exception as err:
            self.logger.error("Failed to list certificates: %s", err)

        for enrollment in enrollments:
            try:
                deployment = self.client.get_cps_production_deployment(enrollment["id"])
                parsed_enrollment = {key: enrollment[key] for key in desired_fields}
                parsed_enrollment["expiry"] = deployment["primaryCertificate"]["expiry"]
                yield parsed_enrollment
            except Exception as err:
                self.logger.error(
                    f"Failed to get deployment for cert '{enrollment['csr']['cn']}': {err}"
                )