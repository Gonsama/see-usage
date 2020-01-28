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
parser.add_argument("--formula", type=str, choices={"shannon", "simpson"}, default = "shannon", help="Diversity index formula we want to use to get diversity: 1.shannon; 2.simpson")
parser.add_argument("--according", type=str, choices={"clients", "members"}, default = "clients", help="The data we want to see the diversity of (clients or members)")
parser.add_argument('--sot', default=False, action='store_true', help="Space between versions (x-axis) scales according to time between them. Default behaviour is equal space between each versions")
parser.add_argument("--o", default="diversity", type=str, help="file name for the output png")
parser.add_argument("--regex", default = "a^", type=str, help="regex defining the versions that we don't want to see on the graph")
args = parser.parse_args()

#########################################
#Getting data to plot (reuse-core sizes)#
#########################################

#getting all versions (path, timestamp) tuple that are not matching regex
versions_tuple = utils.get_sorted_versions_path_timestamp(args.lp, args.regex)

y_data = []

#visit subdirectories one by one to compute the wanted values according to type argument
if args.according == "clients":
    for path,t in versions_tuple:
        clients = utils.get_clients_from_usage(path + "/library-usage.csv")
        diversity = utils.get_diversity_value(clients, args.formula)
        y_data.append(int(diversity * 100))
elif args.according == "members":
    for path,t in versions_tuple:
        members = utils.get_members_from_usage(path + "/library-usage.csv")
        diversity = utils.get_diversity_value(members, args.formula)
        y_data.append(int(diversity * 100))

y_axis_title = "Diversity of " + args.according + " using " + args.formula + "(%)"

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
 
# exact value of dots xritten next to it for further precision
for i in range(0,len(x_axis)): 
    plt.text(x_axis[i], y_data[i],  y_data[i], fontsize=12)

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
