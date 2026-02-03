# pub-routes
An ETL pipeline for getting data from [LTFRB Transport Routes](https://ltfrb.gov.ph/routes-with-consolidated-entities/?utm_source=chatgpt.com)

## Files
- [01.py](./01.py) : Converts the site's HTML data into a jsonl for download. Prints data as it goes
    Output: out.jsonl, Contains the urls and names of files and their regions
- [02.py](./02.py) : Downloads the PDF files 
    Output: PDF files themselves from out.jsonl
- [03.py](./03.py) : Parses the PDF files onto CSVs and saves them. Uses multiprocessing and checks folder Region/{Region Name}/{File Name}
    Output: CSV files from the PDFs in 02.py

## How to Use

1. Download the [LTFRB Transport Routes](https://ltfrb.gov.ph/routes-with-consolidated-entities/?utm_source=chatgpt.com) page as HTML.

2. Run the files
```sh
uv run 01.py
uv run 02.py
uv run 03.py
```

## Notes
- You need to download the LTFRB Transport Routes as HTML as it has CloudFlare bot protection(After checking too, I found out that it uses CF Workers to host the website). [cloudscraper](https://pypi.org/project/cloudscraper/) doesn't work for this as of the writing.
- This is not yet complete. see To-do.
- test/ and filters.md contains data I used when testing various things. Will remove next patch.
- This project is AI-assisted, thorough review has been done before merging the code fixes onto the main code.

## To-do
- [x] Create the main parser
- [ ] Consolidate the entries onto a single file
- [ ] Convert the transport routes onto pathways(or anything that describes the full route) with OpenStreetMap(or related map)

Made with 💙 with kuya-carlo