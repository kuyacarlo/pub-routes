import scrapy

class PublicTranspoRouteSpider(scrapy.Spider):
    name = "LTFRB Route Map"
    start_urls = ["https://ltfrb.gov.ph/routes-with-consolidated-entities/"]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/117.0.0.0 Safari/537.36"
    }


    def parse(self, response):
        for entry in response.css("table.tablepress"):
            head = {
                "name": entry.css("thead > tr > th.column-1::text").get()
            }
            for row in entry.css("tbody.row-striping.row-hover").css("tr"):
                entries = []
                entries.append({
                    "name": row.css("td.column-1::text").get(),
                    "url": row.css('td.column-2 > a::attr("href")').get()
                })
            head["entries"] = entries
            yield head

def main():
    print("Hello from pub-routes!")


if __name__ == "__main__":
    main()
