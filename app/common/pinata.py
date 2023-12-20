import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import unquote
import re
import json

from app.config import settings

def get_filename_from_cd(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return unquote(fname[0])

def upload_to_pinata_using_file(file_content:bytes, file_name:str):
    multipart_data = MultipartEncoder(
        fields={
            'file': (file_name, file_content),
            'pinataMetadata': (None, json.dumps({
                'name': file_name
            }), 'application/json'),
            'pinataOptions': (None, json.dumps({
                'cidVersion': 0
            }), 'application/json')
        }
    )

    headers = {
        'Content-Type': multipart_data.content_type,
        'Authorization': f"Bearer {settings.PINATA_JWT_KEY}" 
    }

    try:
      res = requests.post(
            f"{settings.PINATA_BASE_URL}/pinning/pinFileToIPFS",
            data=multipart_data,
            headers=headers
      )
      data = res.json()
      url = f"ipfs://{data['IpfsHash']}"
      return url
    except Exception as error:
        print(error)
        raise error
    
def upload_metadata_to_pinata(metadata:json, file_name:str):
    
    payload = {
        'pinataContent': metadata,
        'pinataMetadata': {'name': file_name},
        'pinataOptions': { 'cidVersion': 0}
      }
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.PINATA_JWT_KEY}" 
    }

    try:
      res = requests.post(
            f"{settings.PINATA_BASE_URL}/pinning/pinJSONToIPFS",
            json=payload,
            headers=headers
      )
      data = res.json()
      url = f"ipfs://{data['IpfsHash']}"
      return url
    except Exception as error:
        print(error)
        raise error