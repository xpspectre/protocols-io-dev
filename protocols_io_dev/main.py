import os
import logging

from protocols_io_dev.client import ProtocolsClient, ProtocolFilter

this_dir = os.path.dirname(os.path.realpath(__file__))


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(asctime)s : %(name)s : %(message)s')

    # Read credentials from saved location
    creds_file = os.path.join(this_dir, '../.creds')
    with open(creds_file, 'r') as f:
        token = f.read().strip()

    client = ProtocolsClient(token)

    # Start by calling something simple
    profile = client.get_profile()
    print(profile)

    # Query for protocols
    # key = 'plasmid'
    key = 'restriction enzyme'
    protocols = client.list_protocols(ProtocolFilter.public, key)
    print(protocols)

    # Get details on a specific one
    # protocol_id = 90736
    protocol_id = 137
    # protocol_doi = 'dx.doi.org/10.17504/protocols.io.yxmvm3z5bl3p/v1'  # TODO: doesn't work in same way yet

    steps = client.get_protocol_steps(protocol_id)
    print(steps)

    materials = client.get_protocol_materials(protocol_id)
    print(materials)

    return


if __name__ == '__main__':
    main()
