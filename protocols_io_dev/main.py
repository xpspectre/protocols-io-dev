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

    # profile = client.get_profile()
    # print(profile)

    key = 'plasmid'
    # key = 'restriction enzyme'
    protocols = client.list_protocols(ProtocolFilter.public, key)
    print(protocols)

    return


if __name__ == '__main__':
    main()
