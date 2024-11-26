from django.conf import settings
import re


def can_enable_sandbox_mode(to_addresses=[]):
    wants_sandbox_mode = getattr(settings, "SENDGRID_SANDBOX", False)
    if not wants_sandbox_mode:
        return False

    if not to_addresses:
        return True

    domain_whitelist = getattr(settings, "SENDGRID_SANDBOX_WHITELIST_DOMAINS", [])
    regex_whitelist = getattr(settings, "SENDGRID_SANDBOX_WHITELIST_REGEX", [])
    regex_whitelist_compiled = map(re.compile, regex_whitelist)

    for to_address in to_addresses:
        to_address_domain = to_address.split("@")[1]
        if to_address_domain not in domain_whitelist and not any(
            regex.match(to_address) for regex in regex_whitelist_compiled
        ):
            return True  # Return True if any address is not in the whitelist

    return False  # Only return False if all addresses are in the whitelist
