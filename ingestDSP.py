from ext import dspace_rest_client
#from dspace_rest_client import DSpaceRestClient, Collection, Item, Bitstream
from ext import tei_parser
#from tei_parser import TEIParser
import argparse
import time
import os.path
from pathlib import Path
import pprint
from uuid import UUID
import hashlib
import logging

# Set up logging
logging.basicConfig(filename='tei-ingest.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s | %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S')
logger = logging.getLogger('tei-ingest')
pp = pprint.PrettyPrinter(indent=4)

###
# Static functions used in main script execution
###


def md5(fname):
    """
    Calculate md5 checksum of a file, chunked to help with large files
    :param fname: filename to read
    :return: hexdigest of md5 hash
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_existing_bitstreams(existing_item):
    """
    Retrieve metadata for bitstreams already in DSpace for a given item
    :param existing_item: DSpaceRestClient Item object
    :return: dict of bitstream json with the filename as the key
    """
    bitstream_dict = {}
    existing_bitstreams = existing_item.get_bitstreams()
    if existing_bitstreams is not None and len(existing_bitstreams) > 0:
        for existing_bitstream_json in existing_bitstreams:
            if 'name' in existing_bitstream_json:
                bitstream_name = existing_bitstream_json['name']
                bitstream_dict[bitstream_name] = existing_bitstream_json
    return bitstream_dict


def add_or_replace_bitstreams(file_list, added_item):
    """
    Generic function to add bitstreams to a DSpace item. If a file of the same name already exists in DSpace, the
    checksum is compared and the file is then skipped or the contents replaced.
    :param file_list: list of dicts with basic metadata needed to upload and set names, descriptions in DSpace
    :param added_item: DSpaceRestClient Item object
    :return: boolean success flag
    """
    success = True
    handle = added_item.handle
    bitstream_dict = get_existing_bitstreams(added_item)
    for f in file_list:
        if os.path.isfile(f['path']):
            checksum = md5(f['path'])
            if f['name'] in bitstream_dict:
                existing_bitstream_json = bitstream_dict[f['name']]
                if 'checkSum' in existing_bitstream_json and 'value' in existing_bitstream_json['checkSum']:
                    existing_checksum = existing_bitstream_json['checkSum']['value']
                    if checksum != existing_checksum:
                        # Checksums do NOT match: replace bitstream contents
                        existing_bitstream = Bitstream(d, existing_bitstream_json)
                        replace_response = existing_bitstream.update_contents(f['path'])
                        if replace_response is False:
                            logger.error("{}: error replacing file {} for bitstream id {}"
                                         .format(handle, f['name'], existing_bitstream_json['uuid']))
                            success = False
                    else:
                        logger.debug("{}: checksums match, skipping {}".format(handle, f['name']))
                else:
                    logger.warning("{}: no checksum value in {}".format(handle, existing_bitstream_json['name']))
            else:
                logger.debug("{}: no match to existing bitstreams, uploading as new bitstream: {}"
                             .format(handle, f['path']))
                upload_response = added_item.add_bitstream(f['path'], f['name'], f['desc'])
                if upload_response is None:
                    success = False
                #else:
                    # time.sleep(0.05)

    return success


def add_teis(path, item, added_item):
    """
    Compile a list of dicts containing path, name and description of TEI XML files for upload to DSpace
    :param path: base path of TEI XML files
    :param item: prepared item dict (with 'id', 'signatur', 'item' keys)
    :param added_item: DSpaceRestClient Item object
    :return: boolean success
    """
    tei_data = []
    tei_path = path + '/' + item['id']
    xml_file_list = Path(tei_path).glob("*.xml")
    for xml_file in xml_file_list:
        if os.path.isfile(xml_file):
            abs_tei_path = os.path.abspath(xml_file)
            tei_data.append({'path': abs_tei_path, 'name': xml_file.name, 'desc': 'TEI XML'})

    # Add or replace the TEI XML to the passed DSpace item
    success = add_or_replace_bitstreams(tei_data, added_item)
    return success


def add_tiffs(file_paths, item, added_item):
    """
    Compile a list of dicts containing path, name and description of TIFF files for upload to DSpace
    :param path:
    :param item:
    :param added_item:
    :return: boolean success
    """
    # Get simple list of TIFF path data by parsing facsimile.xml and deriving file name
    tiffs = t.parse_facsimile(item['id'])
    tiff_data = []

    for tiff in tiffs:
        # Check all possible paths
        for path in file_paths:
            tiff_path = path + '/' + item['id'] + '/' + tiff['path']
            abs_tiff_path = os.path.abspath(tiff_path)
            if os.path.isfile(tiff_path):
                tiff_data.append({'path': abs_tiff_path, 'name': tiff['name'] + '.tif',
                                       'desc': 'Description of ' + tiff['name']})

    # Add or replace the TIFFs to the passed DSpace item
    success = add_or_replace_bitstreams(tiff_data, added_item)
    return success


"""
###
# Begin main script execution
###

# Define and read command-line arguments
parser = argparse.ArgumentParser(description='Parse TEI XML and submit items to DSpace')
parser.add_argument('-i', '--input', required=True, action='store', dest='input',
                    help='Path of TEI files')
parser.add_argument('-f', '--files', required=True, action='append', nargs='*', dest='files_lists',
                    help='Base path(s) of TIFF files')
parser.add_argument('-s', '--server', required=True, action='store', dest='server',
                    help='Base URL of DSpace REST endpoint, eg. http://localhost:8080/rest')
parser.add_argument('-u', '--user', required=True, action='store', dest='user',
                    help='Username of submitting DSpace user')
parser.add_argument('-p', '--password', required=True, action='store', dest='password',
                    help='Password of submitting DSpace user')
parser.add_argument('-c', '--collection', required=True, action='store', dest='collection',
                    help='Handle of target DSpace collection')
parser.add_argument('-o', '--output', required=False, action='store', dest='output', default='output.csv',
                    help='Path to an (optional) CSV output file containing parsed metadata')
parser.add_argument('--skip-upload', required=False, action='store_false', default=True, dest='upload',
                    help='Skip uploads, just parse TEI XML and produce CSV')
parser.add_argument('--include', required=False, action='store', dest='includes',
                    help='Path to file containing items (folder names) to include, one per line')
parser.add_argument('-v', '--verbose', help='Increase verbosity', dest='verbose', action='count')
args = parser.parse_args()

# Check verbosity and set log level accordingly (-v is INFO, -vv is DEBUG)
if args.verbose is not None:
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)

# Check TEI XML base path is valid
if not os.path.exists(args.input):
    print("ERROR: Input directory does not exist: " + args.input)
    parser.print_usage()
    quit(0)

files_paths = []
if args.files_lists is not None and len(args.files_lists) > 0:
    for args.files_list in args.files_lists:
        for files_path in args.files_list:
            # Check TIFF base path is valid
            if not os.path.exists(files_path):
                print("ERROR: Files input directory does not exist: " + files_path)
                parser.print_usage()
                quit(0)
            else:
                files_paths.append(files_path.rstrip('/'))

# Check includes base path is valid (if it was passed)
include_items = None
if args.includes is not None:
    if os.path.isfile(args.includes):
        with open(args.includes) as f:
            include_items = f.read().splitlines()
    else:
        print("ERROR: Input directory does not exist: " + args.input)
        parser.print_usage()
        quit(0)

# Check handle is (roughly) valid
if "/" not in args.collection:
    print("ERROR: Invalid collection handle: " + args.collection)
    parser.print_usage()
    quit(0)

# Check URL contains http(s) protocol
if "http" not in args.server:
    print("ERROR: Invalid REST URL. Please include the full URL, eg. http://localhost:8080/rest")
    parser.print_usage()
    quit(0)

# Strip trailing slashes from input path
args.input = args.input.rstrip('/')

# Instantiate DSpaceRestClient with basic parameters
d = DSpaceRestClient(user=args.user,
                     password=args.password,
                     rest_url=args.server,
                     verify_ssl=False,
                     load_item_metadata=True)

# Resolve handle parameter to the UUID of target collection
collection_id = d.get_id_by_handle(args.collection)
if collection_id is None or UUID(collection_id) is None:
    logger.critical("could not resolve collection handle to ID: {}".format(args.collection))
    print("ERROR: Could not resolve collection handle to an ID: " + args.collection)
    parser.print_usage()
    quit(0)

start_message = "beginning parse and ingest of {} to DSpace collection: {}".format(args.input, args.collection)
logger.info(start_message)
print(start_message)

# Instantiate TEIParser object
t = TEIParser(args.input, args.output, args.files_list, './fieldnames', include_items)

# Instantiate Collection object
c = Collection(d, {'uuid': collection_id})

# Iterate input directory, parse and crosswalk TEI XML to a list of item dicts with identifiers and metadata
items = t.iterate_xml()
logger.info("number of items parsed from TEI XML: {}".format(len(items)))

# Skip uploads if --skip-upload was passed in command-line
if args.upload:
    for item in items:
        logger.debug("Checking if item already in archive: {}".format(item['signatur']))
        existing_items = d.find_items_by_metadata({'key': 'dc.identifier', 'value': item['signatur']})
        existing_item = None
        if len(existing_items) > 0:
            # We found an existing item
            if len(existing_items) > 1:
                # More than one item with this signatur -- log warning about uniqueness
                logger.critical('{}: this signatur appears as a dc:identifier in {} items. Identifier must be unique!'
                                .format(item['signatur'], len(existing_items)))
                logger.critical('All items with {} will be clobbered with metadata from {}. Correct the idno in '
                                'TEI XML and then re-run this script'.format(item['signatur'], item['id']))

            # We could exit the loop here and log a warning so they are forced to fix uniqueness
            for existing_item_json in existing_items:
                handle = existing_item_json['handle']
                logger.debug("{}: replacing metadata for existing item {}".format(handle, item['id']))

                # Instantiate new Item object from the retrieved item json and call update_item()
                existing_item = Item(d, existing_item_json, c)
                update_response = existing_item.update_item(item['item'])

                # Add, replace, or skip TEI XML and TIFF files
                success = add_teis(args.input, item, existing_item)
                if not success:
                    logger.error("error adding TEI to existing item: ".format(handle))
                success = add_tiffs(args.files_list, item, existing_item)
                if not success:
                    logger.error("error adding TIFFs to existing item: ".format(handle))

        else:
            new_item = c.add_item(item['item'])
            # time.sleep(0.05)
            added_item_json = d.get_item(new_item['uuid'])
            handle = added_item_json['handle']
            logger.debug("Added new DSpace item: {} ({})".format(handle, item['id']))
            if added_item_json is not None:
                added_item = Item(d, added_item_json, c)
                success = add_teis(args.input, item, added_item)
                if not success:
                    logger.error("error adding TEI to new item: {}".format(handle))
                success = add_tiffs(args.files_list, item, added_item)
                if not success:
                    logger.error("error adding TIFFs to new item: {}".format(handle))
            else:
                logger.error("could not retrieve item for newly-added UUID: {}".format(new_item['uuid']))

# Logout DSpace REST
d.logout()
"""