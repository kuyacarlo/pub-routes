from bs4 import BeautifulSoup

with open('ingest/List of Routes with or without Consolidated Entities _ LTFRB.html', 'r') as f:
    soup = BeautifulSoup(f, "html.parser")
def add_urls(data):
    with open('out.jsonl', 'a') as f:
        f.write(str(data) + "\n")

region_data = {}
for table in soup.select("table.tablepress"):
    table_name = table.select_one("thead th.column-1").get_text(strip=True)
    rows = []
    print("-----------------------------------------------------")
    print("Table: ", table_name)
    region_data["table_name"] = table_name
    print("#####################################################")
    for row in table.select("tbody tr"):
        name = row.select_one("td.column-1").get_text(strip=True)
        url = row.select_one("td.column-2 a")["href"]
        print(" Entry:", name, url)
        rows.append({
            "name": name,
            "url": url
            })
    region_data["entries"] = rows
    rows = []
    add_urls(region_data)
    region_data = {}

#print(len(soup.select("table.tablepress")))
