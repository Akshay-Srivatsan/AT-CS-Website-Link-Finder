__author__ = 'Akshay'

import httplib2, sys

# actor = raw_input('Enter an actor name: ')
actor = "Robin Williams"

httplib2.debuglevel = True
http = httplib2.Http('cache')
response, source = http.request('http://www.rottentomatoes.com/celebrity/' + actor.replace(' ', '_').replace('.', ''))

tag_depth = 0
link_indices = []

i = 0
N = len(source)
while i < N:
    if source[i] == '<':
        space = source[i:].find(' ')
        tag_type = source[i+1:i+space]

        close = i + source[i:].find('>')
        tag = source[i:close+1]
        if tag_type == 'a' and ('href="/m/' in tag or 'href="/tv/' in tag) and 'unstyled' in tag and 'articleLink' in tag and 'cfpLinks' not in tag and 'target="_top"' in tag:
            open_end_tag = close + source[close:].find('<')
            close_end_tag = open_end_tag + source[open_end_tag:].find('>')
            link_indices += [[(i, close+1), (open_end_tag, close_end_tag)]]
            i = close_end_tag
        else:
            i = close

    i += 1

# print link_indices

links = map(lambda a: (
    source[a[0][0]:a[0][1]],
    source[a[0][1]:a[1][0]]
),link_indices)

movies = []
tv = []
addresses = []
for link, name in links:
    href = link.find('href')
    startquote = href + link[href:].find('"')
    endquote = startquote + link[startquote+1:].find('"')
    address = link[startquote+1:endquote]
    addresses += [address]
    if '/m/' in address:
        movies += [name]
    else:
        tv += [name]

print actor, "acted in:"
print
print "MOVIES:"
print movies
print
print "TV SHOWS:"
print tv