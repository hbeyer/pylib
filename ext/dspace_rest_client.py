import json
import logging
import requests
from requests import RequestException
import sys
import time
import urllib.parse as urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pprint
pp = pprint.PrettyPrinter(indent=4)

logger = logging.getLogger('dspace-rest-client')

class DSpaceRestClientException(Exception):
    pass


class LoginException(DSpaceRestClientException):
    pass


class LogoutException(DSpaceRestClientException):
    pass


class UpdateItemException(DSpaceRestClientException):
    pass


class AbstractDSpaceObject:
    """ Empty DSpace blueprint object"""
    def __init__(self):
        self.uuid = None
        self.name = None
        self.handle = None
        self.type = None
        self.link = None


class Metadata:
    def __str__(self):
        return json.dumps(self.__dict__)

    def __init__(self, key, value, lang):
        self.key = key
        self.value = value
        self.language = lang


class Bitstream(AbstractDSpaceObject):
    def __str__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])

    def __init__(self, ds_client, bitstream_json):
        super(Bitstream, self).__init__()
        self.ds_client = ds_client

        for k, v in bitstream_json.items():
            self.__setattr__(k, v)

    # if we encounter very large files, look at streaming / chunked upload?
    def update_contents(self, bitstream_path):
        try:
            with open(bitstream_path, 'rb') as f:
                response = requests.put('{}/bitstreams/{}/data'.format(self.ds_client.base_url, self.uuid),
                                    headers=self.ds_client.headers,
                                    cookies={'JSESSIONID': self.ds_client.session},
                                    data=f,
                                    verify=self.ds_client.verify_ssl)
                #logging.info(response)
                #logging.info(response.json())
                if response.status_code != 200:
                    logger.error("Could not update contents for bitstream:{} ".format(self.uuid))
                    return False
                else:
                    return True
        except RequestException:
            logger.info('Could not add bitstream')


class Collection(AbstractDSpaceObject):
    def __str__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])

    def __init__(self, ds_client, item_json):
        super(Collection, self).__init__()
        self.ds_client = ds_client

        for k, v in item_json.items():
            self.__setattr__(k, v)

    def add_item(self, metadata):
        """
        Create a item
        :param metadata:
        :param ds_collection:
        :return:
        """
        item = {  # Structure necessary to create DSpace item
            "type": "item",
            "metadata": metadata
        }

        #logging.info("Item: %s", item)

        collection_url = self.ds_client.base_url + '/collections/' + self.uuid + '/items'
        #logging.info(collection_url)

        # Create item
        try:
            response = requests.post(collection_url,
                                     headers=self.ds_client.headers,
                                     cookies={'JSESSIONID': self.ds_client.session},
                                     data=json.dumps(item),
                                     verify=self.ds_client.verify_ssl)
            if response.status_code != 200:
                logger.error('Could not add metadata to handle: {}'.format(self.handle))
                logger.error(response.status_code)
                logger.error(response.content)

            return json.loads(response.content)

        except RequestException:
            logger.info('Could not create DSpace item: {}'.format(collection_url))


class Item(AbstractDSpaceObject):
    def __str__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])

    def __init__(self, ds_client, item_json, collection=None):
        super(Item, self).__init__()
        self.ds_client = ds_client

        for k, v in item_json.items():
            self.__setattr__(k, v)

        self.lastModified = time.strptime(self.lastModified, "%Y-%m-%d %H:%M:%S.%f")
        self.archived = bool(item_json['archived'])
        self.withdrawn = bool(item_json['withdrawn'])
        self.metadata = self.get_metadata() if self.ds_client.load_item_metadata else None

    def get_metadata(self):
        try:
            response = self.ds_client.request_get('/items/{}/metadata'.format(self.uuid))
        except RequestException:
            logger.error('Could not get metadata for DSpace item: {}'.format(self.handle))

        return [Metadata(m['key'], m['value'], m['language']) for m in response.json()]

    def update_item(self, metadata):
        #item_id = self.get_id_by_handle(self.handle)
        item_id = self.uuid
        try:
            response = requests.put('{}/items/{}/metadata'.format(self.ds_client.base_url, item_id),
                                    headers=self.ds_client.headers,
                                    cookies={'JSESSIONID': self.ds_client.session},
                                    data=json.dumps(metadata),
                                    verify=self.ds_client.verify_ssl)

            if response.status_code != 200:
                raise UpdateItemException()

            logger.info('Updated item {} with {} metadata values.'.format(self.handle, len(metadata)))
            return response

        except UpdateItemException as e:
            logger.error('Could not update DSpace item: {}\n{}'.format(self.handle, e))
        except RequestException:
            logger.error('Could not update DSpace item: {}'.format(self.handle))

    def get_bitstreams(self):
        try:
            response = requests.get('{}/items/{}/bitstreams'.format(self.ds_client.base_url, self.uuid),
                                    headers=self.ds_client.headers,
                                    cookies={'JSESSIONID': self.ds_client.session},
                                    verify=self.ds_client.verify_ssl)
        except RequestException:
            logger.info('Could not get items')

        return response.json()

    def add_bitstream(self, bitstream_path, name, description):
        try:
            with open(bitstream_path, 'rb') as f:
                response = requests.post('{}/items/{}/bitstreams'.format(self.ds_client.base_url, self.uuid),
                                    headers=self.ds_client.headers,
                                    cookies={'JSESSIONID': self.ds_client.session},
                                    params={'name': name, 'description': description},
                                    data=f,
                                    verify=self.ds_client.verify_ssl)
                if response.status_code != 200:
                    raise UpdateItemException()
                logger.debug("added bitstream: {} to item {}".format(name, self.handle))
                return response
        except RequestException:
            logger.info('Could not add bitstream')

    def add_metadata(self, metadata):
        """
        Add metadata to a item
        :param handle:
        :param metadata:
        :return:
        """
        metadata = [m.__dict__ for m in metadata]

        try:
            response = requests.post(self.ds_client.base_url + '/items/' + self.uuid + '/metadata',
                                     headers=self.ds_client.headers,
                                     cookies={'JSESSIONID': self.ds_client.session},
                                     data=json.dumps(metadata),
                                     verify=self.ds_client.verify_ssl)
        except RequestException:
            logger.info('Could not add metadata to item: {}'.format(self.handle))

        if response.status_code != 200:
            logger.error('Could not add metadata to handle: {}'.format(self.handle))
            logger.error(response.status_code)
            logger.error(response.content)

        logger.info('Added {} metadata items to item: {}'.format(len(metadata), self.handle))


class DSpaceRestClient:
    def __init__(self, user, password, rest_url, verify_ssl, load_item_metadata=False):
        # Parameters for establishing connection
        self.user = user
        self.password = password
        self.rest_url = rest_url
        self.verify_ssl = verify_ssl
        self.session = None
        self.headers = {
            'Accept': 'application/json',
            "Content-Type": 'application/json',
        }

        self._parse_and_clean_urls()
        self.base_url = self.rest_url.scheme + '://' + self.rest_url.netloc + self.rest_url.path

        # Parameters for efficiency, i.e. don't get again what you should already have
        self.communities = None
        self.collections = None
        self.items = None
        self.load_item_metadata = bool(load_item_metadata)
        self.bitstreams = None

        self._login()

    def _login(self):
        """
         Log in to get DSpace REST API token.
        :return:
        """
        body = {'email': self.user, 'password': self.password}

        try:
            response = requests.post(self.base_url + '/login',
                                     data=body,
                                     verify=self.verify_ssl)

            if response.status_code != 200:
                raise LoginException()

            logger.info('Logged in to REST API.')
        except LoginException as e:
            logger.error('FATAL Error {} logging in to DSpace REST API, aborting'.format(response.status_code))
            sys.exit(1)
        except RequestException as e:
            logger.error('FATAL Error {} logging in to DSpace REST API, aborting\n{}'.format(response.status_code, e))
            sys.exit(1)

        set_cookie = response.headers['Set-Cookie'].split(';')[0]

        self.session = set_cookie[set_cookie.find('=') + 1:]

    def logout(self):
        """
        Logout from DSpace API
        :return:
        """

        try:
            response = requests.post(self.base_url + '/logout',
                                     headers=self.headers,
                                     cookies={'JSESSIONID': self.session},
                                     verify=self.verify_ssl)

            if response.status_code != 200:
                raise LogoutException()

            logger.info('Logged out of REST API.')
        except LogoutException as e:
            logger.error('Error logging out of DSpace REST API.\n{}'.format(e))
        except RequestException as e:
            logger.error('Error logging out of DSpace REST API.\n{}'.format(e))

    def _parse_and_clean_urls(self):
        self.rest_url = urlparse.urlparse(self.rest_url)

        # KIM - TODO - disabling for now, reenable with config option
        #if self.rest_url.scheme != 'https':
         #   self.rest_url = self.rest_url._replace(scheme='https')

        #if not self.rest_url.port:
         #   self.rest_url = self.rest_url._replace(netloc=self.rest_url.netloc + ":443")

        logger.info('DS REST Cleaned: {}'.format(self.rest_url))

    def request_get(self, url):
        return requests.get(self.base_url + url,
                            headers=self.headers,
                            cookies={'JSESSIONID': self.session},
                            verify=self.verify_ssl)

    def _get(self, rest_url, ds_obj, offset, limit, results=[]):
        """
        Get *
        :param offset:
        :param results:
        :param limit:
        :return:
        """
        response = None
        try:
            response = self.request_get('/{}?offset={}&limit={}'.format(rest_url, offset, limit))
        except RequestException:
            logger.error('Could not get {}'.format(rest_url))

        if response.status_code == 200:
            results = results + [ds_obj(self, obj) for obj in response.json()]

            if offset < limit and len(response.json()) == limit:
                return self._get(rest_url, ds_obj, offset + limit, limit, results)
            else:
                return results
        else:
            return 'Could not get {}. \n{}'.format(rest_url, response.content)

    # Get an item
    def get_item(self, uuid):
        response = json.loads(requests.get(self.base_url + '/items/' + uuid,
                                    headers=self.headers,
                                    cookies={'JSESSIONID': self.session},
                                    verify=False).content)
        return response

    def find_items_by_metadata(self, metadata):
        response = None
        try:
            response = requests.post(self.base_url + '/items/find-by-metadata-field',
                                     headers=self.headers,
                                     cookies={'JSESSIONID': self.session},
                                     data=json.dumps(metadata),
                                     verify=self.verify_ssl)
        except RequestException:
            msg = 'Could not get item for metadata: {}={} ({})'.format(metadata.key, metadata.value, metadata.language)
            logger.info(msg)

        if response.status_code == 200:
            return response.json()

        return None

    def get_id_by_handle(self, handle):
        # Get an ID for a handle
        response = None
        try:
            response = requests.get(self.base_url + '/handle/' + handle,
                                    headers=self.headers,
                                    cookies={'JSESSIONID': self.session},
                                    verify=self.verify_ssl)
        except RequestException:
            msg = 'Could not get id for: {}'.format(handle)
            logger.info(msg)

        if response.status_code == 200:
            return response.json()['uuid']

        return None

    @staticmethod
    def format_metadata(key, value, lang):
        """Reformats the metadata for the REST API."""
        return {'key': key, 'value': value, 'language': lang}
