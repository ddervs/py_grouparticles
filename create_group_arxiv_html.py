import urllib.request, urllib.parse, urllib.error
import feedparser
import json
import toolz

# Base api query url
base_url = 'http://export.arxiv.org/api/query?';

# Search parameters
search_query = 'all:electron' # search for electron in all fields
start = 0                     # retreive the first 5 results
max_results = 5

query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                     start,
                                                     max_results)

# Opensearch metadata such as totalResults, startIndex, 
# and itemsPerPage live in the opensearch namespase.
# Some entry metadata lives in the arXiv namespace.
# This is a hack to expose both of these namespaces in
# feedparser v4.1
feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

### Load group search queries

with open("search_queries.json", "r") as file: 
    entries_dict = json.load(file)

results_concat = []

for item in entries_dict:
    query = 'search_query=%s&start=%i&max_results=%i' % (item['query'],
                                                     item['start'],
                                                     item['max_entries'])

    #perform a GET request using the base_url and query
    response = urllib.request.urlopen(base_url+query).read()

    # parse the response using feedparser
    feed = feedparser.parse(response)
    # print out feed information
    print('Feed title: %s' % feed.feed.title)
    print('Feed last updated: %s' % feed.feed.updated)

    # print opensearch metadata
    print('totalResults for this query: %s' % feed.feed.opensearch_totalresults)
    print('itemsPerPage for this query: %s' % feed.feed.opensearch_itemsperpage)
    print('startIndex for this query: %s'   % feed.feed.opensearch_startindex)
    
    results_concat.append(feed.entries)

### Clean feed data    

flattened = [item for sublist in results_concat for item in sublist]
newlist = sorted(flattened, key=lambda x: x["published"], reverse=True)
uniques = list(toolz.unique(newlist, key=lambda x: x["title"]))

### BUILD HTML
arxiv_max_entries = 50

feed = uniques
#Much of this style is taken from https://arxiv.org/arXiv.css
html = '<div id="arxivcontainer" style=margin:.7em;font-size:90%">\n'
format_name = ''
#Everything is contained in a dl
html += '<dl>\n';
# Add each entry
if (arxiv_max_entries == 0):
    num_entries = len(feed)
    extra_entries = False

elif (arxiv_max_entries >= len(feed)): 
    num_entries = len(feed)
    extra_entries = False
    
else: 
    num_entries = arxiv_max_entries
    extra_entries = True

for x in range(num_entries):
    #Add the numeral in brackets with a space
    html += '<dt>['+str(x+1)+']&nbsp\n'
    #add a span with the ref to the id in it
    html += '\t<span class="list-identifier" style="font-weight:bold"><a href="'+feed[x]['id']+'" title="Abstract">'+feed[x]['id']+'</a>';

    #open a set of divs to contain the various fields
    html+='<dd style="padding-bottom:1em;">\n\t<div class="meta" style="line-height:130%;">\n\t\t<div class="list-title" style="font-size:large;font-weight:bold;margin:0.25em 0 0 0;line-height:120%">\n'
    #Add the title in a span
    html += '\t\t\t'+ feed[x]['title']+'\n\t\t</div>'
    #add authors in a div
    num_authors = len(feed[x]['authors'])
    author_str = feed[x]['authors'][0]['name']
    for i in range(1, num_authors):
        author_str = author_str  + ", " + feed[x]['authors'][i]['name']
        
    author_str = author_str + "."
    html += '\t\t<div class="list-authors" style="font-weight:normal;font-size:110%;text-decoration:none;">'+author_str+'</div>\n';
    
    #Add journal_ref if present and not disabled
    try:
        journal_ref = feed[x]['arxiv_journal_ref']
        html += '\t\t<div class="list-journal-ref" style="font-weight:normal;font-size:90%;"><span class="descriptor">Journal ref:</span> ' + journal_ref + '</div>';
    except:
        continue
    

    #Add and link DOI if present and not disabled (there may be multiple, space separated entries)
    try:
        current_doi = feed[x]['arxiv_doi']
        html += '\t\t<div class="list-doi" style="font-weight:normal;font-size:90%;"><span class="descriptor">DOI:</span> ';
        html += '<a href="https://dx.doi.org/'+current_doi+'">'+current_doi+'</a> ' 
        html += '</div>\n';
    except:
        continue
        
    html += '\t</div>\n</dd>';

#close the arxiv container div
html += '</dl>\n</div>\n'

import sys
print(sys.version)
print(html)

### WRITE FILE

html_filename = "arxiv_group_feed.html" 

with open(html_filename, "w") as writefile:
    writefile.write(html) 
