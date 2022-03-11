import os
from pathlib import Path
import xml.etree.ElementTree as ET
import csv
import pprint
import logging

# init pretty printer for object inspection
pp = pprint.PrettyPrinter(indent=4)

# init logging
logger = logging.getLogger('tei-parser')


class FacsimileParser:
    def __init__(self):
        None


class TEIParser:
    """
    This class handles locating XML files in the input path and mapping TEI XML to
    DSpace (Dublin Core) key/value style metadata
    """
    def __init__(self, input_path, output_csv, tiffs_path, fieldnames_list, include_items):
        """
        Constructor takes input and output paths and a list of fieldnames to include in CSV
        :param input_path:
        :param output_csv:
        :param tiffs_path:
        :param fieldnames_list:
        """
        self.input_path = input_path
        self.output_csv = output_csv
        self.tiffs_path = tiffs_path
        self.fieldnames_list = fieldnames_list
        self.include_items = include_items

    def parse_tei(self, xml_file):
        """
        Parse an XML file, searching for relevant TEI elements and attributes and crosswalking them
        to items in an item_metadata dict
        :param xml_file:
        :return: item_metadata dict
        """

        # Define TEI and XML namespaces
        ns = {'tei': 'http://www.tei-c.org/ns/1.0',
              'xml': 'http://www.w3.org/XML/1998/namespace'}

        infile = xml_file

        # New dict for item metadata
        item_metadata = {'filename': infile}

        # Get document tree
        tree = ET.parse(infile)

        # Get TEI root node
        root = tree.getroot()

        # Get msDesc node
        manuscript_description = root.find('tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc', ns)

        # Get publicationStmt node
        publication_statement = root.find('tei:teiHeader/tei:fileDesc/tei:publicationStmt', ns)

        # Get titleStmt node
        title_statement = root.find('tei:teiHeader/tei:fileDesc/tei:titleStmt', ns)

        m = manuscript_description
        p = publication_statement
        t = title_statement

        if m is None or p is None:
            logger.critical("Required msDesc or publicationStmt TEI elements are missing: {}".format(infile))
            return

        # Title statement
        title = t.find('./tei:title', ns)

        # Licence and rights metadata
        availability = p.find('./tei:availability', ns)
        licence = availability.find('./tei:licence', ns)
        licence_p = availability.find('./tei:licence/tei:p', ns)
        licence_date = licence.get('notBefore') if licence is not None else None
        licence_paras = availability.findall('./tei:licence/tei:p', ns)

        # Extract rights holder and usage statement from the last licence paragraph
        # and reformat rights statement
        rights_para = None
        if licence_paras is not None and len(licence_paras) > 0:
            rights_para = licence_paras.pop()
        rights_holder = rights_para.text.replace(' (', '') if rights_para is not None else None
        rights_usage_ref = rights_para.find('./tei:ref', ns) if rights_para is not None else None
        rights_usage_url = rights_usage_ref.get('target') if rights_usage_ref is not None else None
        rights_usage_text = rights_usage_ref.text if rights_usage_ref is not None else None
        rights_usage = None
        rights_statement = None
        if rights_usage_url is not None and rights_usage_text is not None and rights_holder is not None:
            rights_usage = rights_usage_text + ': ' + rights_usage_url
            rights_statement = rights_holder + ' (' + rights_usage + ')'

        # Publication and publisher details
        publisher = p.find('./tei:publisher/tei:orgName', ns)
        publisher_alt = p.find('./tei:publisher/tei:name[@type="org"]', ns)
        publisher_link = p.find('./tei:publisher/tei:ptr', ns)
        distributor = p.find('./tei:distributor', ns)
        publication_place_purl = p.find('./tei:pubPlace/ptr[@type="purl"]', ns)
        publication_place_thumbnail = p.find('./tei:pubPlace/ptr[@type="thumbnail"]', ns)
        publication_urn = p.find('./tei:idno[@type="URN"]', ns)
        issue_date = p.find('./tei:date[@type="issued"]', ns)
        digitisation_date = p.find('./tei:date[@type="digitised"]', ns)
        nbn = p.find('./tei:idno[@type="URN"]', ns)

        # Identifiers section
        settlement = m.find('./tei:msIdentifier/tei:settlement', ns)
        repository = m.find('./tei:msIdentifier/tei:repository', ns)
        collection = m.find('./tei:msIdentifier/tei:collection', ns)
        idno = m.find('./tei:msIdentifier/tei:idno', ns)
        alt_identifiers = m.findall('./tei:msIdentifier/tei:altIdentifier/tei:idno', ns)
        alternative_alt_identifier = m.find('./tei:msIdentifier/tei:altIdentifier[@type="alternative"]/tei:idno', ns)

        # Construct signatur object
        signatur = ''
        signatur += settlement.text + ', ' if settlement is not None else ''
        signatur += repository.text + ', ' if repository is not None else ''
        signatur += idno.text if idno is not None else ''

        # Head section (alt title, languages, dates and places)
        orig_date = m.find('./tei:head/tei:origDate', ns)
        orig_place = m.find('./tei:head/tei:origPlace', ns)

        # msContents section
        text_lang = m.find('./tei:msContents/tei:textLang', ns)

        # physDesc section
        object_desc = m.find('./tei:physDesc/tei:objectDesc', ns)

        measure = None
        if object_desc is not None:
            support_desc = object_desc.find('./tei:supportDesc', ns)

            if support_desc is not None:
                support_desc_mats = support_desc.find('./tei:support/tei:material/tei:p', ns)
                measure = support_desc.find('./tei:extent/tei:measure', ns)
                dimensions = support_desc.find('./tei:extent/tei:dimensions', ns)
                dimensions_height = dimensions.find('./tei:height', ns) if dimensions is not None else None
                dimensions_width = dimensions.find('./tei:width', ns) if dimensions is not None else None

        # Now, set / construct item_metadata values based on data extracted above
        try:
            # dc.identifier
            item_metadata['dc.identifier'] = signatur if signatur is not None else None

            # dc.identifier.urn
            item_metadata['dc.identifier.urn'] = nbn.text if nbn is not None else None

            # dc.title
            item_metadata['dc.title'] = title.text.replace(' — Signaturdokument', '') if title is not None else None

            # dcterms.license
            item_metadata['dc.rights.uri'] = licence.get('target') if licence is not None else None

            # dcterms.rightsHolder
            item_metadata['dcterms.rightsHolder'] = rights_holder if rights_holder is not None else None

            # dc.publisher
            item_metadata['dc.publisher'] = publisher.text if publisher is not None else None
            if publisher is not None:
                item_metadata['dc.publisher'] = publisher.text
            elif publisher_alt is not None:
                item_metadata['dc.publisher'] = publisher_alt.text
            else:
                item_metadata['dc.publisher'] = None

            # dc.type
            item_metadata['dc.type'] = 'Text'
            if object_desc is not None and object_desc.get('form') is not None:
                item_metadata['dc.type'] += '||' + object_desc.get('form')

            # dc.date
            item_metadata['dc.date'] = issue_date.get('when') if issue_date is not None else None

            # dc.date.embargo
            item_metadata['dc.date.embargo'] = licence_date if licence_date is not None else None

            # dc.creator
            item_metadata['dc.creator'] = None #'TBD'

            # dc.relation
            item_metadata['dc.relation'] = None #'TBD'

            # dc.language
            item_metadata['dc.language'] = text_lang.get('mainlang') if text_lang is not None else None

            # dc.format
            item_metadata['dc.format'] = None #'TBD'

            # dc.subject
            item_metadata['dc.subject'] = None #'TBD'

            # dc.description
            item_metadata['dc.description'] = None #'TBD'

            # dc.contributor
            item_metadata['dc.contributor'] = None #'TBD'

            # dc.rights
            item_metadata['dc.rights'] = rights_statement if rights_statement is not None else None

            # dc.source
            item_metadata['dc.source'] = alternative_alt_identifier.text if alternative_alt_identifier is not None else None

            # dcterms.extent
            item_metadata['dcterms.extent'] = measure.text if measure is not None else None

            # dcterms.isPartOf
            item_metadata['dcterms.isPartOf'] = collection.text if collection is not None else None

        except AttributeError as err:
            logger.error("Couldn't find attribute in one or more vars for {}: {}".format(infile, err))

        return item_metadata

    def parse_facsimile(self, id):
        """
        Parse facsimile.xml files for references to image URLs to construct TIFF filenames/paths
        :param id:
        :return:
        """
        # Define TEI and XML namespaces
        ns = {'tei': 'http://www.tei-c.org/ns/1.0',
              'xml': 'http://www.w3.org/XML/1998/namespace'}

        tiffs = []
        filename = self.input_path + '/' + id + '/facsimile.xml'
        if not os.path.isfile(filename):
            logger.info("{} has no file named: {}".format(id, filename))
            return tiffs

        # Get graphics elements
        tree = ET.parse(filename)
        root = tree.getroot()
        graphics = root.findall('tei:graphic', ns)

        for graphic in graphics:
            jpg_url = graphic.get('url')
            tiff_name = graphic.get('{http://www.w3.org/XML/1998/namespace}id')

            # Pull apart the URL and reconstruct a relative path to the associated TIFF
            url_parts = jpg_url.split('/')
            # Get last part of filename and replace .jpg with .tif in the filename
            tiff = url_parts.pop().replace('jpg', 'tif')
            relative_path = tiff
            tiffs.append({'name': tiff_name, 'path': relative_path})

        return tiffs

    def prepare_item(self, item_metadata):
        """
        Converts the simple item_metadata dict into a list of dicts with 'key' and 'value' keys
        as per DSpace REST item JSON structure
        :param item_metadata:
        :return: JSON-like list of metadata fields and values
        """
        item = list()
        for key in item_metadata:
            if item_metadata[key] is not None and key != 'filename':
                values = str(item_metadata[key]).replace('\t', '').replace('\n', '').replace('\r', '').split('||')
                for value in values:
                    field = {'key': key, 'value': value}
                    item.append(field)
        return item

    def iterate_xml(self):
        logger.info("beginning XML iteration of {}".format(self.input_path))
        with open(self.output_csv, 'w', newline='') as csvfile:
            with open(self.fieldnames_list) as fieldnames_sorted:
                fieldnames = [line.rstrip('\n') for line in fieldnames_sorted]
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writeheader()
            item_list = []
            items = []
            # Iterate over all sub-directories of this path
            path_list = Path(self.input_path).glob("**/")
            for path in path_list:
                path_str = str(path)
                path_id = path.parts[-1]
                # If a valid '--include' argument was passed, check to see if this path_id should be included
                if self.include_items is None or path_id in self.include_items:
                    # Look just for the tei-msDesc.xml filenames
                    xml_file_list = Path(path_str).glob("tei-msDesc.xml")
                    for xml_file in xml_file_list:
                        if os.path.isfile(xml_file):
                            item_metadata = self.parse_tei(xml_file)
                            if item_metadata is not None:
                                item_list.append(item_metadata)
                                items.append({'id': path_id,
                                              'item': self.prepare_item(item_metadata),
                                              'signatur': item_metadata['dc.identifier']})
                                csv_writer.writerow(item_metadata)
                            else:
                                logger.critical("{}: parse error, item_metadata was None for {}"
                                                .format(path_id, xml_file))
                else:
                    logger.info("Skipping directory as it does not appear in 'include' list: {}".format(path_id))

            return items