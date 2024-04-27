import json
import os
import convert_media_catalog
import requests

from getModelsJapan import downloadFile, getBaseResourceURL

data = {}

def download_file(url, local_path):
    """
    Downloads a file from the given URL to the local path.
    """
    response = requests.get(url)
    with open(local_path, "wb") as f:
        f.write(response.content)
        
# 1 for offline, 0 for online but cors issue
_type = 1

option = {
    "skipExisting": True
}

if not (os.path.isdir("./data")):
    os.mkdir("./data")

if __name__ == "__main__":
    base_url = getBaseResourceURL() + '/MediaResources'
    res = base_url + '/MediaCatalog.bytes'
    response = requests.get(res)
    catalog = convert_media_catalog.MediaCatalogBytes(response.content)
    table = catalog.convert_to_dict()
    media_to_download = table['Table']
    # https://prod-clientpatch.bluearchiveyostar.com/r47_1_22_46zlzvd7mur326newgu8_2 + /MediaResources/MediaCatalog.json
    data = {}
    for asset_key in media_to_download:
        asset = media_to_download[asset_key]
        if "Audio/VOC_JP/" in asset["path"] and "MemorialLobby" in asset["path"]:
            key_event = ''.join(asset["path"].split("/")[-1].split(".")[:-1])
            filename = ''.join(asset["path"].split("/")[-1])

            # Download the file
            if _type:
                path = f"./assets/audio/{filename}"
                print("=" * 30)
                print(filename)
                if os.path.isfile(path):
                    print("Already downloaded. Skipping.")
                    data[key_event] = path
                    continue
                os.makedirs(os.path.dirname(path), exist_ok=True)
                download_file(base_url + "/" + asset["path"], path)
                data[key_event] = path
            else:
                # Online version (cors?)
                data[key_event] = base_url + "/" + asset["path"]

    print(data)
    with open("./data/audio.json", "w") as f:
        json.dump(data, f, indent=4)
    print("=" * 30)
    print("Done!")
