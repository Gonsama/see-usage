import utils
import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.dates as md
import random
from datetime import datetime
from scipy.stats.stats import pearsonr

def get_metric_data(versions_tuple, metric, according, formula, percent):
    """Returns a tuple where the first element is a list of data and the secund is the name of the axis that will be used"""
    data = []
    if metric == "nUsages":
        for path,t in versions_tuple:
            nb_rows = utils.get_csv_rows_nb(path + os.path.sep + "library-usage.csv")
            data.append(nb_rows)
            print ("Number of usages for " + path + " is " + str(nb_rows))
        return data, "Number of usages"  
    elif metric == "nClients":
        for path,t in versions_tuple:
            nb_unique_clients = utils.get_unique_clients(path + os.path.sep + "library-usage.csv")
            data.append(nb_unique_clients)
            print ("Number of clients for " + path + " is " + str(nb_unique_clients))
        return data, "Number of clients" 
    elif metric == "nMembers":
        for path,t in versions_tuple:
            nb_unique_used_members = utils.get_unique_used_members(path + os.path.sep + "library-usage.csv")
            data.append(nb_unique_used_members)
            print ("Number of members used for " + path + " is " + str(nb_unique_used_members))
        return data, "Number of members used"
    elif metric == "reusability-index":
        for path,t in versions_tuple:
            members = utils.get_members_from_usage(path + os.path.sep + "library-usage.csv")
            reusability_index = utils.get_reusability_index(members)      
            data.append(reusability_index)
            print ("reusability index for " + path + " is " + str(reusability_index))
        return data, "Reusability Index"
    elif metric == "diversity":
        for path,t in versions_tuple:
            if according == "clients":
                data.append(utils.get_data_to_plot("clients", formula, path))
            elif according == "members":
                data.append(utils.get_data_to_plot("members", formula, path))
        return data, "Diversity of " + according + " using " + formula + "(%)"
    elif metric == "core":
        for path,t in versions_tuple:
            size = utils.get_csv_rows_nb(path + os.path.sep + "reuse-core-" + str(percent) + ".csv")
            data.append(size)
            print ("Reuse-core size of " +  str(percent) + "% for " + path + " is " + str(size))
        return data, "Reuse-core size (alpha = " + str(percent) + " %)"

########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--lp", required=True, type=str, help="path to the repertory of the library (groupid + artifactid)")
parser.add_argument("--metric1", required=True, choices={"nUsages", "nMembers", "nClients", "reusability-index", "diversity", "core"}, default = "nUsages", help="metric that will be on the x-axis")
parser.add_argument("--metric2", required=True, choices={"nUsages", "nMembers", "nClients", "reusability-index", "diversity", "core"}, default = "nUsages", help="metric that will be on the y-axis")
parser.add_argument("--according1", type=str, choices={"clients", "members"}, default = "clients", help="Which data for the diversity index of the first metric")
parser.add_argument("--according2", type=str, choices={"clients", "members"}, default = "clients", help="Which data for the diversity index of the secund metric")
parser.add_argument("--formula1", type=str, choices={"pielou", "simpson", "theil", "gini"}, default = "pielou", help="Diversity index formula we want to use to get diversity for first metric")
parser.add_argument("--formula2", type=str, choices={"pielou", "simpson", "theil", "gini"}, default = "pielou", help="Diversity index formula we want to use to get diversity for secund metric")
parser.add_argument("--percent1", type=int, default = 50, help="Which alpha percent for the reuse-core of the first metric")
parser.add_argument("--percent2", type=int, default = 50, help="Which alpha percent for the reuse-core of the secund metric")
parser.add_argument("--o", default="scatter", type=str, help="file name for the output png")
parser.add_argument("--regex", default = "a^", type=str, help="regex defining the versions that we don't want to see on the graph")
parser.add_argument("--minusages", default=0, type=int, help="define the minimum usages of versions that will be shown")
parser.add_argument("--minclients", default=0, type=int, help="define the minimum unique clients of versions that will be shown")
args = parser.parse_args()

######################
#Getting data to plot#
######################

#getting all versions (path, timestamp) tuple which are not matching regex and which respects the minusages/minclients args  
versions_tuple= utils.get_sorted_versions_path_timestamp(args.lp, args.regex, args.minusages, args.minclients)

#visit subdirectories one by one to compute the wanted values according to type argument
print ("###############################")

print ("Computing first metric for all versions")

data_tuple = get_metric_data(versions_tuple, args.metric1, args.according1, args.formula1, args.percent1)
x_data = data_tuple[0]
x_axis_title = data_tuple[1]
  
print ("###############################")

print ("Computing secund metric for all versions")

data_tuple = get_metric_data(versions_tuple, args.metric2, args.according2, args.formula2, args.percent2)
y_data = data_tuple[0]
y_axis_title = data_tuple[1]

print ("###############################")

pearson_coeff = pearsonr(x_data, y_data)
print ("The pearson correlation value is " + str(pearson_coeff[0]) + " (p= + " + str(pearson_coeff[1]) + ")")

print ("###############################")
######
#Plot#
######

 
# style
plt.style.use('seaborn-darkgrid')
 
# create a color palette
palette = plt.get_cmap('Set1')
    
# scatter plot
plt.scatter(x_data, y_data, color='r')
 
#legend
plt.legend(loc=2, ncol=1)

#titles
plt.title(args.lp, loc='center', fontsize=24, fontweight=0, color='black')
plt.xlabel(x_axis_title)
plt.ylabel(y_axis_title)
plt.tight_layout()
plt.savefig(args.o + '.png')
plt.show()
