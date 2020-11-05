# Download and process files from flickr group
import flickrapi
import requests
import hashlib
import os
import configparser
from timeit import default_timer as timer
from pprint import pprint
import tempfile
from bloom_filter import BloomFilter

config = configparser.ConfigParser()
config.read('pictureframe.config')

flickr_config = config['FLICKR']
api_key = flickr_config['ApiKey']
api_secret = flickr_config['ApiSecret']
photoset_id = flickr_config['Photoset']
group_id = flickr_config['Group']

file_config = config['FILES']
display_dir = file_config['Active']
max_queue_size = file_config.getint('MaxQueue', fallback=200)
bloom_filter_file = file_config.get('BloomFilterFile', fallback='dl.cache')

screen_config = config['SCREEN']
gamma = screen_config.get("Gamma", fallback="1.2")
width = screen_config["Width"]
height = screen_config["Height"]
flipflop = screen_config.getboolean("FlipFlop", fallback=False)
flipflop_cmd = ""
if flipflop:
    flipflop_cmd = "-flip -flop"

flickr = flickrapi.FlickrAPI(api_key, api_secret)

seen_filter = BloomFilter(max_elements=10000, error_rate=0.001, filename=bloom_filter_file)

def process_photo(url, destination):
    print("Processing {}".format(url))
    # Determine if file exists in destination
    dest_file_name = hashlib.sha224(bytearray(url,'utf-8')).hexdigest() + ".bmp"
    dest_file_path = os.path.join(destination, dest_file_name)
    if (not os.path.exists(dest_file_path)):
        # Download file to temporary location
        with tempfile.NamedTemporaryFile(mode='w+b', prefix="flickr-group-", delete=True) as dl_file:
            start = timer()
            r = requests.get(url)
            end = timer()
            print("Downloaded in {} seconds".format(round(end-start,1)))
            dl_file.write(r.content)
            # convert to BMP
            start = timer()
            os.system("convert {} -colorspace gray -contrast -contrast -gamma {} -resize {}x{} -gravity center -extent {}x{} {} {}".format(dl_file.name, gamma, width, height, width, height, flipflop_cmd, dest_file_path))
            end = timer()
            print("Converted in {} seconds".format(round(end-start,1)))
            # Store this file in local database
            

# If the group queue directory is full, exit.
display_dir_size = len([name for name in os.listdir(display_dir) if os.path.isfile(name)])
if display_dir_size >= max_queue_size:
    print("Display directory is full, not attempting to pull new images")
    exit()
# Everytime we run, get the most recent photo from the group, convert it, and store it in the
# group queue.  

print(group_id)
group_photo_page = flickr.groups.pools.getPhotos(group_id=group_id, per_page=100, extras='url_o, url_k')
for results in group_photo_page:
    for photo in results:
        print("Checking photo '{}'".format(photo.get('title')))
        urls = [photo.get('url_o'), photo.get('url_k')]
        url = next((item for item in urls if item is not None), None)
        if url:
            # Check if we have downloaded this before
            if url in seen_filter:
                print("Skipping - downloaded this previously")
            else:
                seen_filter.add(url)
                process_photo(url, display_dir)
        else:
            print("Skipping - large image size not available")
exit()
