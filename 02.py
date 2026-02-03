import json
import os
import gdown

with open("out.jsonl", "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]

for table in data:
    folder = table["table_name"]
    if not os.path.exists(folder):
        os.makedirs(folder)
    for file in table["entries"]:
        file_name = folder + "/" + file["name"] + ".pdf"
        print("Downloading " + file_name)
        file_id = file["url"].split("/d/")[1].split("/")[0]
        download_url = f"https://drive.google.com/uc?id={file_id}"
        try:
            gdown.download(download_url, file_name, quiet=False)
        except gdown.exceptions.FileURLRetrievalError as e:
            print(f"Failed to download {file['url']}: {e}")
