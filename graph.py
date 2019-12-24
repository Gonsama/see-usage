import csv
import argparse
import os
from fnmatch import fnmatch
import matplotlib.pyplot as plt
import matplotlib.dates as md
import requests
import json
import re
import random
from datetime import datetime


def get_timestamp_from_json(json_data):
    """return timestamp of library specified by json data"""
    #format is dict containing 2 keys response and responseheader, the values are also dict
    response_data = json_data["response"]
    docs_data = response_data["docs"]
    #if no timestamp
    if len(docs_data) == 0:
        return 0
    else:
        return docs_data[0]["timestamp"]

def get_timestamp(path):
    """return timestamp of library specified by path"""

    #look for properties file first, if it doesn't exist request REST api for the properties
    if os.path.isfile(path + "/properties.json"):
        print (path + "/properties.json exist")
        with open(path + "/properties.json") as json_file:
            json_data = json.load(json_file)
            return get_timestamp_from_json(json_data)
    else:
        print (path + "/properties.json do not exist" )


    #properties file doesnt exist

    # example of split path : ['csv-data', 'commons-cli', 'commons-cli', '1.3']
    split_path = re.split(':|/',path) 

    url = 'https://search.maven.org/solrsearch/select?q=g:"' + split_path[1] + '"%20AND%20a:"' + split_path[2] + '"%20AND%20v:"' + split_path[3] + '"&wt=json'

    print ("Requesting properties from REST api ...")    

    try:
        myResponse = requests.get(url)
    except requests.exceptions.RequestException as e:
        print (e)
        return 0

    # For successful API call, response code will be 200 (OK)
    if(myResponse.ok):

        print ("Response to get properties of " + path + " is OK")

        # Loading the response data into a dict variable
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        json_data = json.loads(myResponse.content)
        
        #write data in file for next times
        with open( path + '/properties.json', 'w') as outfile:
            json.dump(json_data, outfile)        

        return get_timestamp_from_json(json_data)
    else:
        # If response code is not ok (200)
        print ("Response to get properties of " + path + " is not OK")
        myResponse.raise_for_status()
        return 0 

def remove_library(index):
    """remove library from all dicts and lists related to the final plot"""
    global versions_tuple
    global reuse_core_sizes
    global versions
    versions_tuple.pop(index)
    versions.pop(index)
    for key,value in reuse_core_sizes.items():
        value.pop(index)

########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--lp", required=True, type=str, help="path to the repertory of the library (groupid + artifactid)")
parser.add_argument("--p", nargs="+", type=int, help="Reuse-core percent values we want in plot (1 or more values)")
parser.add_argument('--sot', default=False, action='store_true', help="Space between versions (x-axis) scales according to time between them. Default behaviour is equal space between each versions")
parser.add_argument("--o", default="reuse-core", type=str, help="file name for the output png")
parser.add_argument("--regex", default = "a^", type=str, help="regex defining the versions that we don't want to see on the graph")
args = parser.parse_args()

#########################################
#Getting data to plot (reuse-core sizes)#
#########################################

root_directory = args.lp

#getting all versions (path, timestamp) tuple that are not matching regex
regex = re.compile( args.regex)
versions_tuple= [(x[0],get_timestamp(x[0])) for x in os.walk(args.lp) if x[0] != root_directory and not regex.search(x[0])]

reuse_core_sizes = {}
#init dict key = reuse-core percent, value = list of sizes
for percent in args.p:
    reuse_core_sizes[percent] = []

#sort list so that versions are in ascending order
versions_tuple = sorted(versions_tuple, key=lambda tup: tup[1])

#visit subdirectories one by one to compute the reuse-core sizes
for path,t in versions_tuple:
    for percent in args.p:
        try:
            f = open(path + "/reuse-core-" + str(percent) + ".csv", "r")
            #minus 1 bcs first line is column names        
            size = sum(1 for line in f) - 1
            reuse_core_sizes[percent].append(size)
            f.close()
        except IOError:
            print ("File " + path + "/reuse-core-" + str(percent) + ".csv" + " do not exist. You should use the script to get the reuse-core before proceeding. ")
            exit()

#x-axis of plot will be different according to sot argument
versions = [path.split("/")[2] for path,t in versions_tuple]
if args.sot:
    for tup in versions_tuple:
        #libraries without timestamp are removed to not distort results
        if tup[1] == 0:
            remove_library(versions_tuple.index(tup))
            
    x_axis = []
    for i in range(len(versions_tuple)-1,-1,-1):
        #rare case where two versions have the same timestamp
        if len(x_axis) >= 1 and versions_tuple[i][1] == x_axis[0]: 
            x_axis.insert(0,versions_tuple[i][1] - 1)
        else:
            x_axis.insert(0,versions_tuple[i][1])
    x_axis_title = "time"
else:
    #space between versions will be equal
    #split path to versions to get only versions
    x_axis = versions
    x_axis_title = "library version"

######
#Plot#
######

 
# style
plt.style.use('seaborn-darkgrid')
 
# create a color palette
palette = plt.get_cmap('Set1')
    

#if x_axis is time, we have to change the format to date (converting from timestamp)
if args.sot:
    plt.gca().xaxis.set_major_formatter(md.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(md.YearLocator())
    #have to divide timestamp by 1000 to convert from milliseconds to seconds
    x_axis = [datetime.fromtimestamp(t / 1000) for t in x_axis]   

# multiple line plot
num=0
for percent,sizes in reuse_core_sizes.items():
    num+=1
    plt.plot(x_axis, sizes, marker='o', color=palette(num), linewidth=1, alpha=0.9, label="p = " + str(percent))

#if x_axis is time, we have to put the library version to at teast one set of points (random set)
if args.sot:
    random_value_from_dict = random.choice(list(reuse_core_sizes.values()))
    for i in range(0,len(x_axis)): 
        plt.text(x_axis[i], random_value_from_dict[i],  versions[i], fontsize=9)
 
#legend
plt.legend(loc=2, ncol=1)

#vertical x-axis 
plt.xticks(rotation=45)
plt.tight_layout()

#titles
plt.title(root_directory, loc='center', fontsize=24, fontweight=0, color='red')
plt.xlabel(x_axis_title)
plt.ylabel("reuse-core size")
plt.savefig(args.o + '.png')
plt.show()
