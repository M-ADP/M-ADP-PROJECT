import pytest
from pydantic import ValidationError

from src.app.dns.schemas import DNSCreate, DNSUpdate


def test_dns_create_normalizes_subdomain_to_lowercase() -> None:
    payload = DNSCreate(subdomain="My-App")

    assert payload.subdomain == "my-app"


@pytest.mark.parametrize("subdomain", ["app!", "my_app", "a.b"])
def test_dns_create_rejects_invalid_characters(subdomain: str) -> None:
    with pytest.raises(ValidationError):
        DNSCreate(subdomain=subdomain)


@pytest.mark.parametrize("subdomain", ["-start", "end-"])
def test_dns_create_rejects_hyphen_edge_positions(subdomain: str) -> None:
    with pytest.raises(ValidationError):
        DNSCreate(subdomain=subdomain)


def test_dns_update_has_same_validation_rules() -> None:
    with pytest.raises(ValidationError):
        DNSUpdate(subdomain="invalid!")

    payload = DNSUpdate(subdomain="New-Sub")
    assert payload.subdomain == "new-sub"
