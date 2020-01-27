import utils
import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.dates as md
import random
from datetime import datetime


########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--lp", required=True, type=str, help="path to the repertory of the library (groupid + artifactid)")
parser.add_argument("--p", nargs="+", type=int, help="Reuse-core percent values we want in plot (1 or more values)")
parser.add_argument("--type",type=int, choices={1, 2}, default = 1, help="Type of plot: 1.evolution of reuse-core-size; 2.evolution of ratio reuse-core-size/total-used-api-size")
parser.add_argument('--sot', default=False, action='store_true', help="Space between versions (x-axis) scales according to time between them. Default behaviour is equal space between each versions")
parser.add_argument("--o", default="graph", type=str, help="file name for the output png")
parser.add_argument("--regex", default = "a^", type=str, help="regex defining the versions that we don't want to see on the graph. For example, ... means the libraries containing beta in their name shouldn't be plot")
args = parser.parse_args()

#########################################
#Getting data to plot (reuse-core sizes)#
#########################################

#getting all versions (path, timestamp) tuple that are not matching regex
versions_tuple = utils.get_sorted_versions_path_timestamp(args.lp, args.regex)

y_data = {}
#init dict key = reuse-core percent, value = list of sizes
for percent in args.p:
    y_data[percent] = []

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
if args.sot:
    for tup in versions_tuple:
        #libraries without timestamp must be removed to not distort results
        if tup[1] == 0:
            index = versions_tuple.index(tup)
            versions_tuple.pop(index)
            for key,value in y_data.items():
                value.pop(index)

x_axis_data = utils.get_x_axis_data(args.sot, versions_tuple)
x_axis = x_axis_data[0]
x_axis_title = x_axis_data[1]

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

#if x_axis is time, we have to put the library version to at least one set of points (random set)
if args.sot:
    versions = [path.split("/")[2] for path,t in versions_tuple]
    random_value_from_dict = random.choice(list(y_data.values()))
    for i in range(0,len(x_axis)): 
        plt.text(x_axis[i], random_value_from_dict[i],  versions[i], fontsize=9)
 
#legend
plt.legend(loc=2, ncol=1)

#vertical x-axis 
plt.xticks(rotation=45)
plt.tight_layout()

#titles
plt.title(args.lp, loc='center', fontsize=24, fontweight=0, color='red')
plt.xlabel(x_axis_title)
plt.ylabel(y_axis_title)
plt.savefig(args.o + '.png')
plt.show()
