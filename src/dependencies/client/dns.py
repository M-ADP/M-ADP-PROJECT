from src.core.client.dns import DnsClient
from src.common.config.dns_server import get_dns_config
from src.infra.client import DnsClientImpl


def get_dns_client() -> DnsClient:
    return DnsClientImpl(dns_server_config=get_dns_config())
