import scrapy
import pandas as pd
import os

class ListingsSpider(scrapy.Spider):
    name = 'listings'
    start_urls = [
        'https://www.privateproperty.co.za/for-sale/gauteng/johannesburg/bedfordview/41?tp=2000000&pt=5,2,10&sorttype=1',
        'https://www.privateproperty.co.za/for-sale/gauteng/johannesburg/fourways-sunninghill-and-lonehill/27?tp=2000000&pt=5,2,10&sorttype=1',
        'https://www.privateproperty.co.za/for-sale/gauteng/johannesburg/johannesburg-south/26?tp=2000000&pt=5,2,10&sorttype=1',
        'https://www.privateproperty.co.za/for-sale/gauteng/johannesburg/north-riding-to-lanseria/1928?tp=2000000&pt=5,2,10&sorttype=1',
        'https://www.privateproperty.co.za/for-sale/gauteng/johannesburg/northcliff/36?tp=2000000&pt=5,2,10&sorttype=1',
        'https://www.privateproperty.co.za/for-sale/gauteng/johannesburg/randburg-and-ferndale/35?tp=2000000&pt=5,2,10&sorttype=1',
        'https://www.privateproperty.co.za/for-sale/gauteng/johannesburg/rosebank-and-parktown/38?tp=2000000&pt=5,2,10&sorttype=1',
        'https://www.privateproperty.co.za/for-sale/gauteng/johannesburg/sandton-and-bryanston-north/34?tp=2000000&pt=5,2,10&sorttype=1'
    ]

    def parse(self, response):
        # Extract data from the current page
        items = self.extract_listing_info(response)

        # Save data to CSV using pandas
        df = pd.DataFrame(items)
        df.to_csv('listings.csv', index=False, mode='a', header=not os.path.exists('listings.csv'))  # Append mode

        # Follow pagination links to scrape all pages for the current suburb
        pagination_links = response.css('a.pageNumber[href*=page]::attr(href)').getall()
        for link in pagination_links:
            yield response.follow(link, self.parse)

        # Follow links in the href column to scrape additional details
        for href in df['href']:
            yield response.follow(href, callback=self.parse_details)

    def extract_listing_info(self, response):
        items = []
        listings = response.css('a.listingResult.row')
        for listing in listings:
            title = listing.css('.title::text').get()
            href = response.urljoin(listing.attrib['href'])
            price = listing.css('.priceDescription::text').get()
            property_type = listing.css('.propertyType::text').get()

            item = {
                'title': title.strip() if title else None,
                'href': href,
                'price': price.strip() if price else None,
                'property_type': property_type.strip() if property_type else None,
            }

            items.append(item)
        return items

    def parse_details(self, response):
        # Extract more information from the detail page

        main_features = {}
        main_feature_elements = response.css('.mainFeatures .mainFeature')
        for element in main_feature_elements:
            label = element.css('strong::text').get().strip()
            value = element.xpath('text()').get().strip().replace('\xa0', ' ')
            main_features[label] = value

        key_main_features = {}
        features = response.css('.features .attribute')
        for feature in features:
            label = feature.css('.attributeLabel::text').get().strip()
            value = feature.css('.propAttrValue::text').get().strip()
            key_main_features[label] = value

        # Create a DataFrame for the new information
        details = {
            'href': response.url,
            'main_features': main_features,
            'key_main_features': key_main_features
        }

        # Append to listings_scrapy.csv
        df = pd.DataFrame([details])
        df.to_csv('listings_scrapy.csv', mode='a', index=False, header=not os.path.exists('listings_scrapy.csv'))

# Run the spider
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    # Create a CrawlerProcess
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'csv',  # No need for FEED_URI here
    })

    # Start the Spider
    process.crawl(ListingsSpider)
    process.start()
