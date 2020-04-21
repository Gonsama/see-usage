import utils
import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.dates as md
import random
from datetime import datetime

def get_data_to_plot(according, formula, path):
    """return diversity index according to arguments"""
    if according == "clients":
        data = utils.get_clients_from_usage(path + "/library-usage.csv")
    elif according == "members":
        data = utils.get_members_from_usage(path + "/library-usage.csv")
    diversity = utils.get_diversity_value(data, formula)
    diversity_percent = int(diversity * 100)        
    print (formula + " index according to " + according + " for " + path + " is " + str(diversity_percent) + "%")
    return diversity_percent

########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--lp", required=True, type=str, help="path to the repertory of the library (groupid + artifactid)")
parser.add_argument("--formula", type=str, choices={"pielou", "simpson", "theil", "gini"}, default = "pielou", help="Diversity index formula we want to use to get diversity: 1.pielou; 2.simpson; 3.theil; 4.gini")
parser.add_argument("--according", type=str, choices={"clients", "members", "clients/members"}, default = "clients", help="The data we want to see the diversity of (clients or members or both)")
parser.add_argument('--sot', default=False, action='store_true', help="Space between versions (x-axis) scales according to time between them. Default behaviour is equal space between each versions")
parser.add_argument("--o", default="diversity", type=str, help="file name for the output png")
parser.add_argument("--regex", default = "a^", type=str, help="regex defining the versions that we don't want to see on the graph. For example, .*beta.*$ means the libraries containing beta in their name shouldn't be plotted")
args = parser.parse_args()

##########################################
#Getting data to plot (diversity indexes)#
##########################################

#getting all versions (path, timestamp) tuple that are not matching regex
versions_tuple = utils.get_sorted_versions_path_timestamp(args.lp, args.regex)

y_data_clients = []
y_data_members = []

#visit subdirectories one by one to compute the wanted values according to type argument
print ("###############################")
print ("computing diversity indexes ...")
for path,t in versions_tuple:
    if args.according == "clients":
        y_data_clients.append(get_data_to_plot("clients", args.formula, path))
    elif args.according == "members":
        y_data_members.append(get_data_to_plot("members", args.formula, path))
    elif args.according == "clients/members":
        y_data_clients.append(get_data_to_plot("clients", args.formula, path))
        y_data_members.append(get_data_to_plot("members", args.formula, path))

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

# unique line plot or two if according argument is equal to clients/members
if len(y_data_clients) > 0:
    plt.plot(x_axis, y_data_clients, marker='o', color=palette(0), linewidth=1, alpha=0.9, label="clients")
if len(y_data_members) > 0:
    plt.plot(x_axis, y_data_members, marker='o', color=palette(1), linewidth=1, alpha=0.9, label="members")
 
# version written next to dot if sot argument is chosen
if args.sot:
    versions = [path.split("/")[2] for path,t in versions_tuple]
    for i in range(0,len(x_axis)): 
        plt.text(x_axis[i], y_data_clients[i],  versions[i], fontsize=9)

#range of y axis changed to begin so that it does show between 0 and 100 percent
x1,x2,y1,y2 = plt.axis()
plt.axis((x1,x2,-5,105))

#legend
if args.according == "clients/members":
    plt.legend(loc='best',
          fancybox=True, shadow=True, ncol=1)
else:
    plt.legend().remove()

#vertical x-axis 
plt.xticks(rotation=90)

#titles
plt.title(args.lp, loc='center', fontsize=24, fontweight=0, color='black')
plt.xlabel(x_axis_title)
plt.ylabel(y_axis_title)
plt.tight_layout()
plt.savefig(args.o + '.png')
plt.show()
