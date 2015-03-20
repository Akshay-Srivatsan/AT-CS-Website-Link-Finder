__author__ = 'Akshay'

import httplib2
import socket
import sys
import time
from multiprocessing import Pool, Value

start_time = time.time()
#
# origin = "http://en.memory-alpha.org/wiki/Paramount_Stage_9"
# target = "http://en.memory-alpha.org/wiki/Sainte_Claire"
# origin = "http://en.memory-alpha.org/wiki/DeForest_Kelley"
# target = "http://en.memory-alpha.org/wiki/Leonard_McCoy"

# Distance = 3; Uses tardis, memory-alpha, and memory-beta wikias. 13 seconds
# origin = 'http://tardis.wikia.com/wiki/Star_Trek'
# target = 'http://memory-beta.wikia.com/wiki/Borg'

# origin = 'http://la.wikipedia.org/wiki/Vicipaedia:Salve'
# target = 'http://la.wikipedia.org/wiki/Compendium'

origin = 'http://google.wikia.com/wiki/Material_Design'
target = 'http://google.wikia.com/wiki/Google'

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
        relative = ''
        # protocol = base_url.split('://')[0]
    if '://' in base_url:
        protocol = base_url.split('://')[0]
        base_url = base_url.split('://')[1]
    if relative.startswith('/'):
        base_url = base_url.split('/')[0] + relative
    elif relative != '':
        base_url = '/'.join(base_url.split('/')[:-1]) + '/' + relative
    base_url = protocol + '://' + base_url
    return (base_url + ('?' + mobile_flag if mobile_flag not in base_url else ''))

origin = assemble_url(origin)
target = assemble_url(target)

if origin == target:
    print 'invalid inputs'
    sys.exit()

# print assemble_url('http://en.memory-alpha.org/wiki/Doctor_Who', 'http://tardis.wikia.com/wiki/The_Doctor')
# sys.exit(0)

def get_source(url):
    try:
        http = httplib2.Http()
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


class Website(object):
    def __init__(self, url, history):
        self.url = url
        self.history = history

    def __str__(self):
        return 'Website'  # self.url.split('/')[-1].split('?')[0]


current_urls = [Website(origin, [])]  # map(lambda x: Website(x, [origin]), extract_links(origin, get_source(origin)))
scanned_urls = []  # [(origin, [])]
urls_to_scan = []
done = Value('i', False)
count_urls_scanned = Value('i', 0)

def scan_url(url, history):
    global done, count_urls_scanned
    _count.value += 1
    if _count.value % 50 == 0:
        print _count.value, 'urls scanned'
    distance = float('inf')
    path = []
    if done.value or url in scanned_urls:
        return {'urls': [], 'distance':float('inf'), 'path':[]}

    temp = map(lambda x: Website(x, history + [url]), extract_links(url, get_source(url)))

    for i in range(0, len(temp)):
        current_url = temp[i]
        if current_url.url == target:
            distance = len(current_url.history)
            path = current_url.history
            done.value = True
    return {'urls': temp, 'distance':distance, 'path':path}

def scan_url_helper(bundle):
    return scan_url(bundle.url, bundle.history)

count = 1
pool = Pool()
while target_distance == float('inf') and len(scanned_urls) < 100000:
    print 'starting level', count
    print 'scanning', len(current_urls), 'urls'

    if target_distance == float('inf'):
        threads = []
        # print current_urls
        mapped = pool.map(scan_url_helper, current_urls)
        print 'done crawling'

        print len(mapped), 'urls to search'

        __count = 0
        def helper(x, y):
            global __count
            part1 = x[0]
            part2 = x[1]
            __count += 1
            if __count % 50 == 0:
                print __count, 'urls searched'
            # print '*', sys.getsizeof(x)
            return part1 + y['urls'], (part2 if part2[0] < y['distance'] else (y['distance'], y['path']))

        urls_to_scan, temp = reduce(
            helper,
            mapped, ([], (float('inf'), [])))

        distance, path = temp

        print 'done searching urls'

        if distance < target_distance:
            target_distance = distance
            target_path = path

        print 'done with level', count
        print '-'*50

    for url in current_urls:
        scanned_urls += [url.url]
    current_urls = urls_to_scan
    urls_to_scan = []

    count += 1
        # print current_url
pool.terminate()

target_path += [target]

end_time = time.time()

time_spent = end_time - start_time


print
print
print 'Origin:', origin.split('?')[0]
print 'Target:', target.split('?')[0]
print 'Distance:', target_distance
print 'Path:',
print '\n\t'.join([''] + map(lambda x: x.split('?')[0], target_path))
print 'Elapsed time:', '%02d:%02d' % divmod(time_spent, 60)