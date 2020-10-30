# Synchronize a Flickr Album locally, and convert for e-ink display.
import flickrapi
import requests
import hashlib
import os
import configparser
from timeit import default_timer as timer


config = configparser.ConfigParser()
config.read('pictureframe.config')

flickr_config = config['FLICKR']
api_key = flickr_config['ApiKey']
api_secret = flickr_config['ApiSecret']
user = flickr_config['User']
album = flickr_config['Album']

file_config = config['FILES']
downloads = file_config['Downloads']
display_dir = file_config['Active']

screen_config = config['SCREEN']
colors = screen_config["Colors"]
gamma = screen_config.get("Gamma", fallback="1.2")
width = screen_config["Width"]
height = screen_config["Height"]
flipflop = screen_config.getboolean("FlipFlop", fallback=False)
flipflop_cmd = ""
if flipflop:
    flipflop_cmd = "-flip -flop"

flickr = flickrapi.FlickrAPI(api_key, api_secret)

# Get all the names of files in downloads/display dir.
# Later, if we haven't seen those from flickr, delete them.
jpeg_files = os.listdir(downloads)
bmp_files = os.listdir(display_dir)

active_base_names = []

for photo in flickr.walk_set(album, per_page=100, extras='url_o'):
    title = photo.get('title')
    url = photo.get('url_o')
    # hash url
    base_file_name = hashlib.sha224(bytearray(url,'utf-8')).hexdigest()
    active_base_names.append(base_file_name)
    file_name = base_file_name + ".jpg"
    jpg_file_path = os.path.join(downloads, file_name)
    bmp_file_path = os.path.join(display_dir, base_file_name+".bmp")
    if ((not os.path.exists(jpg_file_path)) or (not os.path.exists(bmp_file_path))):
        print("Saving {} ...".format(title))
        start = timer()
        r = requests.get(url)
        end = timer()
        print("Downloaded in {} seconds".format(round(end-start,1)))
        with open(jpg_file_path, 'wb') as f:
            f.write(r.content)
        # convert to BMP
        start = timer()
        # Removed -colorspace Gray
        os.system("convert {} -colorspace gray -ordered-dither o8x8 -colors {} -contrast -contrast -gamma {} -resize {}x{} -gravity center -extent {}x{} {} {}".format(jpg_file_path, colors, gamma, width, height, width, height, flipflop_cmd, bmp_file_path))
        end = timer()
        print("Converted in {} seconds".format(round(end-start,1)))
    else:
        print("Image {} already exists, skipping.".format(title))

# remove known files from jpeg/bmp file listing
for a in active_base_names:
    j = a+".jpg"
    b = a+".bmp"
    if j in jpeg_files:
        jpeg_files.remove(j)
    if b in bmp_files:
        bmp_files.remove(b)

print("JPEGs to remove: {}".format(jpeg_files))
print("BMPs to remove: {}".format(bmp_files))
        
# Now delete anything that wasn't found in flickr
for j in jpeg_files:
    try:
        print("removing {}".format(j))
        os.remove(os.path.join(downloads,j))
    except:
        print("Could not find file! {}".format(os.path.join(downloads,j)))
for b in bmp_files:
    try:
        print("removing {}".format(b))
        os.remove(os.path.join(display_dir,b))
    except:
        print("Could not find file! {}".format(os.path.join(display_dir,b)))
    

