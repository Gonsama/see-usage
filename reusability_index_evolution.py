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
parser.add_argument('--sot', default=False, action='store_true', help="Space between versions (x-axis) scales according to time between them. Default behaviour is equal space between each versions")
parser.add_argument("--o", default="reusability-index", type=str, help="file name for the output png")
parser.add_argument("--regex", default = "a^", type=str, help="regex defining the versions that we don't want to see on the graph")
args = parser.parse_args()

############################################
#Getting data to plot (reusability indexes)#
############################################

#getting all versions (path, timestamp) tuple that are not matching regex
versions_tuple = utils.get_sorted_versions_path_timestamp(args.lp, args.regex)

y_data = []

#visit subdirectories one by one to compute the wanted values according to type argument
print ("###############################")
print ("computing reusability indexes ...")
for path,t in versions_tuple:
    members = utils.get_members_from_usage(path + "/library-usage.csv")
    reusability_index = utils.get_reusability_index(members)      
    y_data.append(reusability_index)
    print ("reusability index for " + path + " is " + str(reusability_index))

y_axis_title = "Reusability index"

#x-axis of plot will be different according to sot argument
if args.sot:
    for tup in versions_tuple:
        #libraries without timestamp must be removed to not distort results
        if tup[1] == 0:
            index = versions_tuple.index(tup)
            versions_tuple.pop(index)
            y_data.pop(index)

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

# unique line plot
plt.plot(x_axis, y_data, marker='o', color=palette(0), linewidth=1, alpha=0.9)
 
# version written next to dot if sot argument is chosen
if args.sot:
    versions = [path.split("/")[2] for path,t in versions_tuple]
    for i in range(0,len(x_axis)): 
        plt.text(x_axis[i], y_data[i],  versions[i], fontsize=9)
# exact value of dots written next to it for further precision otherwise
else:
    for i in range(0,len(x_axis)): 
        plt.text(x_axis[i], y_data[i],  y_data[i], fontsize=12)

#range of y axis changed to begin at 0
x1,x2,y1,y2 = plt.axis()
plt.axis((x1,x2,0,y2))

#legend
plt.legend(loc=2, ncol=1)

#vertical x-axis 
plt.xticks(rotation=90)

#titles
plt.title(args.lp, loc='center', fontsize=24, fontweight=0, color='black')
plt.xlabel(x_axis_title)
plt.ylabel(y_axis_title)
plt.tight_layout()
plt.savefig(args.o + '.png')
plt.show()
