"""
imagecrawling

Usage:
  imagecrawling crawl <url> <path> [--depth=-1]
  imagecrawling -h | --help
  imagecrawling --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  imagecrawling crawl

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/adamsaleh/imagecrawling
"""

import requests
import shutil
import os

from inspect import getmembers, isclass
from docopt import docopt
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def getUrlsAndImagesForNetLocation(url):
    page = requests.get(url.geturl())
    soup = BeautifulSoup(page.content, 'html.parser')
    return getUrlsFromSoup(url,soup), getImagesFromSoup(url,soup)

def getUrlsFromSoup(url,soup):
    urls = soup.find_all('a')
    hrefset = {urlparse(link.get('href'))._replace(fragment='') for link in urls}
    
    FQDN = { href for href in hrefset 
                 if href.scheme in ['http','https',''] and url.netloc in href.netloc}
    
    local = {href._replace(scheme=url.scheme,netloc=url.netloc) for href in hrefset
                 if href.netloc is '' and  href.path.startswith('/')}
    
    return local | FQDN

def getImagesFromSoup(url, soup):
    images = soup.find_all('img')
    return {img.get('src') for img in images}

def crawlUrlsAndImagesForNetLocation(url, depth=-1):
    urls = set()
    images = set()
    try:
        new_urls, images = getUrlsAndImagesForNetLocation(url)
    except Exception as e:
        print("Problem while scraping ", url)
        print(e)
    urls |= new_urls
    current_depth = 0
    while depth<0 or depth>=current_depth:
        current_depth+=1
        process_urls = new_urls - urls 
        urls |= new_urls
        new_urls = set()
        if process_urls == set() :
            return urls, images
        else:
            for current_url in process_urls:
                try:
                  current_new_urls, current_new_images = getUrlsAndImagesForNetLocation(current_url)
                except Exception as e:
                  print("Problem while scraping ", current_url)
                  print(e)
                for i in current_new_images:
                  print("Found ", i)
                new_urls |= current_new_urls
                images |= current_new_images
                
    return urls, images

def download_file_to(url, path):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    local_path = os.path.join(path, local_filename)
    with open(local_path, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return local_path

def main():
    """Main CLI entrypoint."""
    options = docopt(__doc__, version="0.1")
    
    if options["crawl"]:
        url = urlparse(options["<url>"])
        path = options["<path>"]
        depth = -1
        if options["--depth"]:
          depth = int(options["--depth"])

        print(depth)

        urls, images = crawlUrlsAndImagesForNetLocation(url,depth)
        for image in images:
          print("Downloading ", image)
          try:
            download_file_to(image,path)
          except Exception as e:
            print("Problem while downloading:", image, " to ", path)
            print(e)

