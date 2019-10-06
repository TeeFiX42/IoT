import netifaces


def get_gateway(interface):
    # Function to retrieve the def. gateway for a given interface.
    for gateway in netifaces.gateways()[netifaces.AF_INET]:
        if gateway[1] == interface:
            return gateway[0]


def create_port_dict():
    # Create a dictionary with the mac addresses of all interfaces.
    address_dict = {}
    for interface in netifaces.interfaces():
        try:
            if "lo" not in interface:
                address_dict[interface] = {"IPv4": netifaces.ifaddresses(interface)[netifaces.AF_INET][0]["addr"],
                                           "MAC": netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]["addr"]}
        except KeyError:
            try:
                address_dict[interface] = {"IPv4": "",
                                           "MAC": netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]["addr"]}
            except KeyError:
                pass
    return address_dict
