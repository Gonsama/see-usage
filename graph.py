import utils
import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.dates as md
import re
import random
from datetime import datetime


def remove_library(index):
    """remove library from all dicts and lists related to the final plot"""
    global versions_tuple
    global y_data
    global versions
    versions_tuple.pop(index)
    versions.pop(index)
    for key,value in y_data.items():
        value.pop(index)

########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--lp", required=True, type=str, help="path to the repertory of the library (groupid + artifactid)")
parser.add_argument("--p", nargs="+", type=int, help="Reuse-core percent values we want in plot (1 or more values)")
parser.add_argument("--type",type=int, choices={1, 2}, default = 1, help="Type of plot: 1.evolution of reuse-core-size; 2.evolution of ratio reuse-core-size/total-used-api-size")
parser.add_argument('--sot', default=False, action='store_true', help="Space between versions (x-axis) scales according to time between them. Default behaviour is equal space between each versions")
parser.add_argument("--o", default="graph", type=str, help="file name for the output png")
parser.add_argument("--regex", default = "a^", type=str, help="regex defining the versions that we don't want to see on the graph")
args = parser.parse_args()

#########################################
#Getting data to plot (reuse-core sizes)#
#########################################

root_directory = args.lp

#getting all versions (path, timestamp) tuple that are not matching regex
regex = re.compile( args.regex)
versions_tuple = []
for x in os.walk(args.lp):
    if x[0] != root_directory and not regex.search(x[0]) and utils.get_csv_rows_nb(x[0] + "/library-usage.csv") != 0:
        timestamp = utils.get_timestamp(x[0])
        if timestamp != -1:        
            versions_tuple.append((x[0],timestamp))
y_data = {}
#init dict key = reuse-core percent, value = list of sizes
for percent in args.p:
    y_data[percent] = []

#sort list so that versions are in ascending order
versions_tuple = sorted(versions_tuple, key=lambda tup: tup[1])

#visit subdirectories one by one to compute the wanted values according to type argument
if args.type == 1:
    for path,t in versions_tuple:
        for percent in args.p:
            size = utils.get_csv_rows_nb(path + "/reuse-core-" + str(percent) + ".csv")
            y_data[percent].append(size)
    y_axis_title = "reuse-core-size"
elif args.type == 2:
    for path,t in versions_tuple:
        for percent in args.p:
            reuse_core_size = utils.get_csv_rows_nb(path + "/reuse-core-" + str(percent) + ".csv")
            total_used_api_size = utils.get_unique_used_members(path + "/library-usage.csv")
            ratio = reuse_core_size / float(total_used_api_size)
            y_data[percent].append(ratio)
    y_axis_title = "RATIO reuse-core-size / total-used-api-members"

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
for percent,sizes in y_data.items():
    num+=1
    plt.plot(x_axis, sizes, marker='o', color=palette(num), linewidth=1, alpha=0.9, label="p = " + str(percent))

#if x_axis is time, we have to put the library version to at teast one set of points (random set)
if args.sot:
    random_value_from_dict = random.choice(list(y_data.values()))
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
plt.ylabel(y_axis_title)
plt.savefig(args.o + '.png')
plt.show()
