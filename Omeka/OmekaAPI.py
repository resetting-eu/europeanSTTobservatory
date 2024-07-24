import requests, re
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="omekaResettingGeoLoc")


# Type of Element Name, Type of Element ID
TITLE_ELEMENT = ["Title", 50]
SUBJECT_ELEMENT = ["Subject", 49]
DESCRIPTION_ELEMENT = ["Description", 41]
CREATOR_ELEMENT = ["Creator", 39]
LOCAL_URL_ELEMENT = ["Local URL", 6]
CONTRIBUTOR_ELEMENT = ["Contributor", 37]
ADDRESS_ELEMENT = ["Address", 54]

SEGITTUR_CATALOGUE_V2 = ("Catalogue of TechnoloCatalogue of Technological Solutions for Smart Tourist Destinations - "
                         "Second Edition")
SEGITTUR_CATALOGUE_V3 = "Catalogue of Technological Solutions for Smart Destinations - Third Edition"
SCOTTISH_CATALOGUE = "Technology solutions for tourism businesses in a post-Covid19 Scotland"
EU_CATALOGUE_2022 = "Leading examples of Smart Tourism Practices in Europe (2022)"
EU_CATALOGUE_2023 = "Leading examples of Smart Tourism Practices in Europe (2023)"
ADESTIC_CATALOGUE_V1 = "Technological Solutions for Tourism (Version 1)"
ADESTIC_CATALOGUE_V2 = "Technological Solutions for Tourism (Version 2)"

STT_TYPE = {
    "id": 21,
    "url": "https://sttobservatory.omeka.net/api/item_types/21",
    "name": "STT",
    "resource": "item_types"
}
STT_APPLICATION_TYPE = {
    "id": 22,
    "url": "https://sttobservatory.omeka.net/api/item_types/22",
    "name": "STT Application",
    "resource": "item_types"
}


def get_metadata_element_set_definition():
    return {'id': 3, 'url': 'https://sttobservatory.omeka.net/api/element_sets/3', 'name': 'Item Type Metadata'}


# def get_hyperlink_item_type():
#     return {'id': 11, 'url': 'https://sttobservatory.omeka.net/api/item_types/11', 'name': 'Hyperlink',
#             'resource': 'item_types'}


def get_type_of_element_definition(type_of_element):
    """json format for the type of element name and id"""
    return {'id': type_of_element[1], 'name': type_of_element[0]}


def add_element(element_text, type_of_element):
    """json format for element to be added to element_texts"""
    if type_of_element[0] == LOCAL_URL_ELEMENT[0]:
        if len(element_text) == 1:
            text = f"<a href={element_text[0]}>{element_text[0]}</a>"
            # print(f"Add URL element: {text}")
        else:
            text = "<ul>"
            for url in element_text:
                text += f"<li><a href={url}>{url}</a></li>"
            text += "</ul>"
    else:
        text = f"<p>{element_text}</p>"
    dic = {'html': True,
           'text': text,
           'element': get_type_of_element_definition(type_of_element),
           'element_set': get_metadata_element_set_definition()
           }
    return dic


def create_json_item(title, description, item_type, urls=None, tags=None, creator=None, collection=None,
                     address=None):
    if tags is None:
        tags = []
    data = {}
    element_texts = [add_element(title, TITLE_ELEMENT), add_element(description, DESCRIPTION_ELEMENT)]

    if collection is not None:
        data["collection"] = {"id": collection}
    if urls is not None:
        element_texts.append(add_element(urls, LOCAL_URL_ELEMENT))
    if creator is not None:
        element_texts.append(add_element(creator, CREATOR_ELEMENT))
    if address is not None:
        element_texts.append(add_element(address, ADDRESS_ELEMENT))

    data.update({
        "public": True,
        "item_type": item_type,
        "tags": tags,
        "element_texts": element_texts
    })
    return json.dumps(data)


def get_multipart_to_add_file(item_id, filename, file):
    """multipart data to add a file to an item"""
    boundary = 'E19zNvXGzXaLvS5C'
    item = {"item": {"id": item_id}}

    multipart_data = MultipartEncoder(
        fields={
            'data': json.dumps(item),
            'file': (filename, file)
        },
        boundary=boundary
    )

    return multipart_data


class OmekaAPI:
    collections_endpoint = "collections"
    items_endpoint = "items"
    geolocations_endpoint = "geolocations"
    files_endpoint = "files"

    def __init__(self, url, api_key):
        self.api_url = f"{url}/api"
        self.api_key = api_key

    def __get_api_url_with_token_for_endpoint__(self, endpoint):
        """The API URL with API KEY it's needed for superuser tasks"""
        return f"{self.api_url}/{endpoint}?key={self.api_key}"

    def __get_api_url_for_endpoint__(self, endpoint):
        return f"{self.api_url}/{endpoint}"

    def __get_all_elements_from_endpoint__(self, endpoint):
        """
        If the endpoint:
         - is items, it will return all items
         - is collections, it will return all collections
         - is geolocations, it will return all geolocations
        """
        return json.loads(requests.get(self.__get_api_url_for_endpoint__(endpoint)).text)

    def post_item(self, title, description, item_type, urls=None, tags=None, creator=None, collection=None,
                  address=None):
        """Create a new item in Omeka and returns his ID"""
        response = requests.post(self.__get_api_url_with_token_for_endpoint__(self.items_endpoint),
                                 data=create_json_item(title, description, item_type, urls, tags, creator, collection,
                                                       address))
        item_id = json.loads(response.text)["id"]
        print(f"\nPost Item for {title}, {item_id}: {response.reason}")
        return item_id

    def post_file_for_item(self, item_id, filename, file):
        """Add a file to an Omeka item. File can be an image, a PDF, ..."""
        multipart_data = get_multipart_to_add_file(item_id, filename, file)
        response = requests.post(self.__get_api_url_with_token_for_endpoint__(self.files_endpoint),
                                 headers={'Content-Type': multipart_data.content_type}, data=multipart_data)
        print(f"Post File to Item {item_id}: {response.reason}")
        return response

    def get_collection_id_by_name(self, collection_name):
        """If it returns -1, it means that the collection doesn't exist"""
        collections = self.__get_all_elements_from_endpoint__(self.collections_endpoint)
        for collection in collections:
            for element_text in collection['element_texts']:
                if element_text['element']['name'] == 'Title':
                    title = re.sub(re.compile('<.*?>'), '', element_text['text'])
                    if title == collection_name:
                        return collection['id']
        return -1

    def get_geolocation_id_by_address(self, address):
        """If it returns -1, it means that the geolocation has not been created yet"""
        locations = self.__get_all_elements_from_endpoint__(self.geolocations_endpoint)
        for geo in locations:
            if geo["address"] == address:
                return geo["id"]
        return -1

    def post_geolocation_for_item(self, address, item_id):
        """Create a new geolocation in Omeka"""
        location = geolocator.geocode(address)
        data = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "address": address,
            "zoom_level": 15,
            "map_type": "Leaflet",
            "extended_resources": [],
            "item": {"id": item_id}
        }
        response = requests.post(self.__get_api_url_with_token_for_endpoint__(self.geolocations_endpoint),
                                 data=json.dumps(data))
        print(f"Post Geolocation to Item {item_id}: {response.reason}")
        return response, json.dumps(data)

    def delete_item(self, item_id):
        response = requests.delete(self.__get_api_url_with_token_for_endpoint__(f"{self.items_endpoint}/{item_id}"))
        print(f"Delete Item {item_id}: {response.reason}")
        return response

    def delete_all_items_from_a_collection(self, collection_name):
        """
        The HTTP request Get has a size limit. So, the function __get_all_elements_from_endpoint__ may not return all
        the items. Therefore, it may be necessary to invoke this function more than once to delete all the items.
        """
        collection_id = self.get_collection_id_by_name(collection_name)
        all_items = self.__get_all_elements_from_endpoint__(self.items_endpoint)

        for item in all_items:
            if "collection" in item:
                if item["collection"] is not None and item["collection"]["id"] == collection_id:
                    self.delete_item(item["id"])
