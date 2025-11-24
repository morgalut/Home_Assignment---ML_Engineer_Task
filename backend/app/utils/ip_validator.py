import ipaddress

def validate_ip(ip: str) -> bool:
    """
    More robust IP validator:
    - Ensures IPv4 or IPv6 correctness
    - Rejects private, loopback, reserved, and multicast IPs
    - Prevents bogon ranges often used in attacks
    """
    try:
        parsed = ipaddress.ip_address(ip)

        # Reject private/internal networks
        if parsed.is_private:
            return False

        # Reject loopback (127.x.x.x, ::1)
        if parsed.is_loopback:
            return False

        # Reject reserved or documentation ranges
        if parsed.is_reserved or parsed.is_unspecified:
            return False

        # Reject multicast addresses
        if parsed.is_multicast:
            return False

        return True

    except ValueError:
        return False
