from django.conf import settings

def get_sandbox_bypass_whitelist():
    # @deprecated - use SENDGRID_SANDBOX_BYPASS_WHITELIST instead
    sandbox_whitelist_domains = getattr(
        settings, "SENDGRID_SANDBOX_WHITELIST_DOMAINS", []
    )
    sandbox_bypass_whitelist = getattr(
        settings, "SENDGRID_SANDBOX_BYPASS_WHITELIST", []
    )
    for sandbox_whitelist_domain in sandbox_whitelist_domains:
        sandbox_bypass_whitelist.append(sandbox_whitelist_domain)
    return list(set(sandbox_bypass_whitelist)) # Ensure unique

def can_bypass_sandbox_setting(to_address, sandbox_bypass_whitelist):
    to_address_domain = to_address.split('@')[1]
    return (
        to_address in sandbox_bypass_whitelist
        or to_address_domain in sandbox_bypass_whitelist
    )

# Note that sandbox mode setting will be bypassed if ANY match is found in the 
# whitelist, not if ALL "to" addresses match
def can_enable_sandbox_mode(to_addresses = []):
    wants_sandbox_mode = getattr(settings, "SENDGRID_SANDBOX", False)
    if not wants_sandbox_mode:
        return False
    sandbox_bypass_whitelist = get_sandbox_bypass_whitelist()
    for to_address in to_addresses:
        if can_bypass_sandbox_setting(to_address, sandbox_bypass_whitelist):
            return False
    return True
