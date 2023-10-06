import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

# element name, element id
TITLE_ELEMENT = ["Title", 50]
SUBJECT_ELEMENT = ["Subject", 49]
DESCRIPTION_ELEMENT = ["Description", 41]
CREATOR_ELEMENT = ["Creator", 39]
URL_ELEMENT = ["URL", 28]
CONTRIBUTOR_ELEMENT = ["Contributor", 37]


def def_elementSet():
    """it's necessary to add the element_set when the element is a URL"""
    return {'id': 3, 'url': 'https://resettingstt.omeka.net/api/element_sets/3', 'name': 'Item Type Metadata'}


def def_itemType_hyperlink():
    """"it's also necessary to add the item_type when the element is a URL"""
    return {'id': 11, 'url': 'https://resettingstt.omeka.net/api/item_types/11', 'name': 'Hyperlink',
            'resource': 'item_types'}


def def_element(typeOfElement):
    """json format for the element name and for element id"""
    return {'id': typeOfElement[1], 'name': typeOfElement[0]}


def add_element(element_text, typeOfElement):
    """json format for element to be added to element_texts"""
    if typeOfElement[0] == "URL":
        dic = {'html': True, 'text': f"<a href={element_text}>{element_text}</a>",
               'element': def_element(typeOfElement),
               'element_set': def_elementSet()}
    else:
        dic = {'html': False, 'text': element_text, 'element': def_element(typeOfElement)}
    return dic


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


def create_json_item(title, description, creator, contributor, url, tags, collection=None):
    data = {}
    if collection is not None:
        data["collection"] = {"id": collection}
    data.update({
        "public": True,
        "item_type": def_itemType_hyperlink(),
        "tags": tags,
        "element_texts": [
            add_element(title, TITLE_ELEMENT),
            add_element(description, DESCRIPTION_ELEMENT),
            add_element(creator, CREATOR_ELEMENT),
            add_element(contributor, CONTRIBUTOR_ELEMENT),
            add_element(url, URL_ELEMENT)
        ]
    })
    return json.dumps(data)


class Omeka:

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def post(self, endpoint, post_data):
        """Create a new item in Omeka"""
        # print(post_data)
        response = requests.post(f"{self.url}/{endpoint}?key={self.api_key}", data=post_data)
        print(f"Post Item{response}")
        return json.loads(response.text)

    def post_file(self, multipart_data):
        """Add a file to an Omeka item"""
        full_url = f"{self.url}/files?key={self.api_key}"
        response = requests.post(full_url, headers={'Content-Type': multipart_data.content_type}, data=multipart_data)
        print(f"Post File to Item: {response}")
