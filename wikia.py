__author__ = 'Akshay'

import threading
import httplib2
import socket
import sys
import time

origin = "http://en.memory-alpha.org/wiki/James_T._Kirk"
target = "http://en.memory-alpha.org/wiki/Robert_Wise"
target_distance = float('inf')
target_path = []

current_urls = []
scanned_urls = []
urls_to_scan = []

scanned = 0

mobile_flag = 'useskin=wikiamobile'
current = origin

urls = []
threadcount = 0

threading.stack_size(32*1024)


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
    time.sleep(10)
    print threadcount
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

class crawlerThread(threading.Thread):
    def __init__(self, url, depth=0, history=[]):
        global threadcount
        threadcount += 1
        threading.Thread.__init__(self)
        self.depth = depth
        self.url = url
        self.history = history + [url]

    def run(self):
        time.sleep
        global urls, target_distance, target_path, target, scanned, threadcount
        if len(urls) % 100 == 0 and scanned != len(urls):
            scanned = len(urls)
            print 'Scanned', len(urls), 'URLs.'
            print threadcount, 'threads currently working.'
        if self.url in urls or self.depth > 6 or target_distance != float('inf'):
            return
        if self.url == target:
            if self.depth < target_distance:
                target_distance = self.depth
                target_path = self.history
            threadcount -= 1
            return
        urls += [self.url]
        links = extract_links(self.url, get_source(assemble_url(self.url)))
        if target in links:
            t = crawlerThread(target, self.depth+1, self.history)
            t.start()
            t.join()
        else:
            threads = []
            for link in links:
                thread = crawlerThread(link, self.depth+1, self.history)
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
                del thread
        threadcount -= 1



t = crawlerThread(origin)
t.start()

t.join()

print
print
print 'Origin:', origin
print 'Target:', target
print 'Distance:', target_distance
print 'Path:',
print '\n\t'.join([''] + target_path)