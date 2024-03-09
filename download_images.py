# Import necessary libraries
import scrapy
import pandas as pd
import os
from bs4 import BeautifulSoup

# Load sold properties data from CSV
file_path = "https://raw.githubusercontent.com/Nikhil-Lakha/HouseFlipping/main/Sold%20Properties/All%20Sold%20Properties.csv"
sold_properties = pd.read_csv(file_path)

# Define the directory path for sold house images
directory_path = 'https://github.com/Nikhil-Lakha/HouseFlipping/tree/main/Sold%20House%20Images'

# List all folders in the directory
folder_list = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]

# Remove rows from sold_properties DataFrame based on the "Listing Number" column
df_filtered = sold_properties[~sold_properties['Listing Number'].isin(folder_list)]

# Define a Scrapy Spider to scrape image URLs from href links
class ImageSpider(scrapy.Spider):
    name = 'image_spider'

    # Start URLs are the href links from df_filtered
    start_urls = df_filtered['href'].tolist()

    def parse(self, response):
        # Extract image URLs and listing number from href links
        listing_number = response.url.split('/')[-1]
        soup = BeautifulSoup(response.text, 'html.parser')
        image_tags = soup.find_all('a', class_='gridImage modalLink lazyLoad')
        for tag in image_tags:
            image_url = tag['data-background']
            yield {
                'listing_number': listing_number,
                'href': response.url,
                'image_url': image_url
            }

# Run the Scrapy Spider
from scrapy.crawler import CrawlerProcess

# Set the output file name
csv_file_path = 'image_links.csv'

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'csv',  # Change output format to CSV
    'FEED_URI': csv_file_path  # Set the output file path
})

process.crawl(ImageSpider)
process.start()

# Now you can read the CSV file into a DataFrame if needed
df_output = pd.read_csv(csv_file_path)
