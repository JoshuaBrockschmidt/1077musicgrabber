#!/usr/bin/env python3

#TODO: 

import json, os, shutil, sys, urllib3
from html.parser import HTMLParser

configFn = 'config.json'
url = 'http://www.1077theend.com/download'
headers = urllib3.util.make_headers(keep_alive=True, user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6')

# Load config information
try:
    with open(configFn, 'r') as f:
        config = json.load(f)
except:
    sys.exit('Error loading config from {}'.format(os.path.abspath(configFn)))

if not config['output_dir']:
    sys.exit('Config file {} is incomplete'.format(os.path.abspath(configFn)))

try:
    if not os.path.exists(config['output_dir']):
        os.makedirs(config['output_dir'])
except:
    sys.exit('Could not create directory {}'.format(os.path.abspath(config['output_dir'])))

http = urllib3.PoolManager()

# Find download link
req = http.request('GET', url, headers=headers)
pageLines = req.data.decode('utf-8').splitlines()

class DLLinkFinder(HTMLParser):
    validFileExts = ['flac', 'mp3', 'ogg', 'wav']
    dllink = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for att in attrs:
                attType = att[0]
                if attType == 'href':
                    link = att[1]
                    for ext in self.validFileExts:
                        if link.endswith(ext):
                            self.dllink = link
                            break
                    break

parser = DLLinkFinder()
for line in pageLines:
    parser.feed(line)
    if parser.dllink != None:
        break
dllink = parser.dllink
parser.close()

# Check if sound file is already downloaded
musicFn = dllink[dllink.rfind('/')+1:]
musicPath = config['output_dir'] + '/' + musicFn
if os.path.isfile(musicPath):
    print('{} has already been downloaded'.format(musicFn))
else:
    # Download sound file
    print('Downloading {}...'.format(parser.dllink))
    with http.request('GET', dllink, preload_content=False) as r, open(musicPath, 'wb') as outFile:
        shutil.copyfileobj(r, outFile)
    print('Done')
