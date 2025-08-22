import requests
from datetime import datetime
import os
import logging
import csv
import re


pattern = re.compile(r'10\.\S+')
url_pattern = re.compile(r'^(https?://\S+)$')
doi_pattern = re.compile(r'^10\.\d{4,9}\/[-._;()/:a-zA-Z0-9]+$')


def fix_doi(input: str):
    return input.replace("%2F", "/")


class ObisDoi:

    def __init__(self):
        self.title = None
        self.publicationYear = datetime.now().year
        self.url = None
        self.doi = None
        self.prefix = "10.25607"
        self.suffix = None
        self.types = {
            "ris": "DATA",
            "bibtex": "misc",
            "citeproc": "project",
            "schemaOrg": "Project",
            "resourceTypeGeneral": "Project"
        }
        self.creators = [
            {
                "name": "Ocean Biodiversity Information System (OBIS)",
                "nameType": "Organizational",
            }
        ]
        self.publisher = "Ocean Biodiversity Information System (OBIS)"

        
    def reserve(self):
        payload = {
            "data": {
                "attributes": {
                    # "event": "publish", #this is commented so it will be a draft record
                    "prefix": self.prefix,
                    "types": self.types,
                    "doi": self.doi,
                    "creators": self.creators,
                    "titles": [{
                        "title": self.title
                    }],
                    "publisher": self.publisher,
                    "publicationYear": datetime.now().year,
                    "url": self.url,
                }
            }
        }

        headers = {
            "Content-Type": "application/vnd.api+json"
        }
        print("Payload being sent to DataCite:")
        print(payload)
        response = requests.post("https://api.datacite.org/dois", json=payload, headers=headers, auth=(os.getenv("DOI_USER"), os.getenv("DOI_PASSWORD")))

        print("Response from DataCite:")
        print(response.status_code, response.text)
        return(response.json())