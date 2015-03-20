__author__ = 'Akshay'

import threading
import httplib2
import socket
import sys
import time
from multiprocessing import Pool
#
origin = "http://en.memory-alpha.org/wiki/Paramount_Stage_9"
target = "http://en.memory-alpha.org/wiki/Sainte_Claire"
origin = "http://en.memory-alpha.org/wiki/DeForest_Kelley"
target = "http://en.memory-alpha.org/wiki/Leonard_McCoy"
target_distance = float('inf')
target_path = []

current_urls = []
scanned_urls = []
urls_to_scan = []

scanned = 0
current_level = 0

mobile_flag = 'useskin=wikiamobile'
current = origin

urls = []
threadcount = 0


def assemble_url(base_url, relative=''):
    protocol = 'http'
    if relative.startswith('http'):
        base_url = relative
        protocol = base_url.split('://')[0]
    if '://' in base_url:
        protocol = base_url.split('://')[0]
        base_url = base_url.split('://')[1]
    if relative.startswith('/'):
        base_url = base_url.split('/')[0] + relative
    elif relative != '':
        base_url = '/'.join(base_url.split('/')[:-1]) + '/' + relative
    base_url = protocol + '://' + base_url
    return base_url + ('?' + mobile_flag if mobile_flag not in base_url else '')

origin = assemble_url(origin)
target = assemble_url(target)

def get_source(url):
    try:
        http = httplib2.Http('cache')
        response, source = http.request(url)
        return source if response.status == 200 else ''
    except socket.error as error:
        sys.exit(1)

def extract_links(url, source):
    links = []
    i = 0
    N = len(source)
    in_script = False
    while i < N:
        if source[i] == '<':
            start_open_tag = i
            end_open_tag = i + source[i:].find('>')
            end_tag_type = i + source[i:].find(' ')
            if end_tag_type < 0 or end_tag_type > end_open_tag:
                end_tag_type = end_open_tag

            tag_type = source[i+1:end_tag_type]
            tag = source[i+1:end_open_tag]
            if tag_type == 'script' or tag_type == 'footer':
                in_script = True
            if tag_type == '/script' or tag_type == '/footer':
                in_script = False

            if not in_script:
                if tag_type == 'a':
                    href_start = tag.find('href="')+6
                    href_end = href_start + tag[href_start:].find('"')
                    href = tag[href_start:href_end]
                    followable = 'rel="nofollow"' not in tag
                    part_of_body = 'subnav' not in tag and 'title' in tag and 'accesskey' not in tag
                    if followable and part_of_body:
                        links += [assemble_url(url, href)]
        i += 1
    return links


current_urls = map(lambda x: (x, [origin]), extract_links(origin, get_source(origin)))
scanned_urls = [(origin, [])]
urls_to_scan = []

#
# def scan_url(url, history):
#     global urls_to_scan
#     urls_to_scan += map(lambda x: (x, history + [url]), extract_links(url, get_source(url)))


def scan_url(url, history):
    global target_distance, target_path
    if target_distance != float('inf') or url in scanned_urls:
        return []

    temp = map(lambda x: (x, history + [url]), extract_links(url, get_source(url)))

    for i in range(0, len(temp)):
        current_url = temp[i]
        if current_url[0] == target and len(current_url[1]) < target_distance:
            print 'Hello'
            target_distance = len(current_url[1])
            target_path = current_url[1]
    return temp

def scan_url_helper(bundle):
    return scan_url(bundle[0], bundle[1])

count = 0
pool = Pool()
while target_distance == float('inf') and len(scanned_urls) < 1000:
    print 'starting level', count
    print 'scanning', len(current_urls), 'urls'

    print 'done checking for matches'

    if target_distance == float('inf'):
        threads = []
        # for current_url in current_urls:
        #     thread = threading.Thread(target=lambda: scan_url(current_url[0], current_url[1]))
        #     thread.start()
        #     threads += [thread]
        #     scanned_urls += [current_url]
        #
        # print 'scanning level', count
        # for thread in threads:
        #     thread.join()
        #     thread.terminate()
        #     del thread
        urls_to_scan = reduce(lambda x, y: x + y, pool.map(scan_url_helper, current_urls))
        print 'scanned level', count

    current_urls = urls_to_scan
    urls_to_scan = []

    count += 1
        # print current_url

target_distance += 1
target_path += [target]


print
print
print 'Origin:', origin
print 'Target:', target
print 'Distance:', target_distance
print 'Path:',
print '\n\t'.join([''] + target_path)