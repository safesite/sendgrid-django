from django.conf import settings
import re

# Note that sandbox mode "True" setting will be bypassed if ANY match is found in the 
# whitelist, not if ALL to_addresses match.
def can_enable_sandbox_mode(to_addresses = []):
    wants_sandbox_mode = getattr(settings, "SENDGRID_SANDBOX", False)
    if not wants_sandbox_mode:
        return False
    domain_whitelist = getattr(settings, "SENDGRID_SANDBOX_WHITELIST_DOMAINS", [])
    regex_whitelist = getattr(settings, "SENDGRID_SANDBOX_WHITELIST_REGEX", [])
    regex_whitelist_compiled = map(re.compile, regex_whitelist)
    for to_address in to_addresses:
        to_address_domain = to_address.split('@')[1]
        if (
            to_address_domain in domain_whitelist
            or any(regex.match(to_address) for regex in regex_whitelist_compiled)
        ):
            return False # Don't allow Sandbox mode even though it's value is True
    return True
