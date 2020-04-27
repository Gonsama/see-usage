import utils
import argparse
import os
import matplotlib.pyplot as plt
import numpy as np

def my_autopct(pct):
    return ('%1.1f%%' % pct) if pct > 1 else ''

########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--lp", required=True, type=str, help="path to the repertory of the library (groupid + artifactid)")
parser.add_argument("--type",type=str, choices={"usages", "members", "clients"}, default = "usages", help="Type of plot: number of usages (data), number of unique api-members or number of unique clients")
parser.add_argument('--pie', default=False, action='store_true', help="plot the repartition on a pie chart according to percentage for each versions")
parser.add_argument("--o", default="repartition", type=str, help="file name for the output png")
parser.add_argument("--regex", default = "a^", type=str, help="regex defining the versions that we don't want to see on the graph. For example, .*beta.*$ means the libraries containing beta in their name shouldn't be plotted")
parser.add_argument("--minusages", default=0, type=int, help="define the minimum usages of versions that will be shown")
parser.add_argument("--minclients", default=0, type=int, help="define the minimum unique clients of versions that will be shown")
args = parser.parse_args()

#########################################
#Getting data to plot (reuse-core sizes)#
#########################################

root_directory = args.lp

#getting all versions (path, timestamp) tuple which are not matching regex and which respects the minusages/minclients args  
versions_tuple= utils.get_sorted_versions_path_timestamp(args.lp, args.regex, args.minusages, args.minclients)

print ("###############################")
print ("computing repartitions ...")

#visit subdirectories one by one to compute the wanted values (number of rows for each version)
y_data = []
if args.type == "usages":
    y_axis_title = "number of usages"
    for path,t in versions_tuple:
        nb_rows = utils.get_csv_rows_nb(path + "/library-usage.csv")
        y_data.append(nb_rows)
        print ("Number of usages for " + path + " is " + str(nb_rows))
elif args.type == "members":
    y_axis_title = "number of unique members"
    for path,t in versions_tuple:
        nb_unique_used_members = utils.get_unique_used_members(path + "/library-usage.csv")
        y_data.append(nb_unique_used_members)
        print ("Number of members for " + path + " is " + str(nb_unique_used_members))
elif args.type == "clients":
    y_axis_title = "number of unique clients"
    for path,t in versions_tuple:
        nb_unique_clients = utils.get_unique_clients(path + "/library-usage.csv")
        y_data.append(nb_unique_clients)
        print ("Number of clients for " + path + " is " + str(nb_unique_clients))

#space between versions will be equal
#split path to get only versions
versions = [path.split("/")[2] for path,t in versions_tuple]
x_axis = versions

x_axis_title = "library version"

######
#Plot#
######

# style
plt.style.use('seaborn-darkgrid')

if args.pie:
    #tuple of format (version, y_data)
    version_repartition_tuple = [(x_axis[i], y_data[i]) for i in range(len(y_data))]
    #sort list according to second element which is the value of the repartition in descending order
    sorted_tuple = sorted(version_repartition_tuple, key=lambda tup: tup[1], reverse=True)
    fig1, ax1 = plt.subplots()
    y_data = [tup[1] for tup in sorted_tuple]
    x_axis = [tup[0] for tup in sorted_tuple]
    total_data = 0
    for data in y_data:
        total_data += data
    for i in range(len(y_data)):
        if y_data[i] / total_data * 100  < 1:
            x_axis[i] = '' 
    ax1.pie(y_data, labels=x_axis, autopct=my_autopct, startangle=90, textprops={'fontsize': 8})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Repartition of " + args.type, loc='center', fontsize=16, fontweight=0, color='black')
    plt.tight_layout()
else: 
    #bar chart
    x_pos = np.arange(len(x_axis))
    plt.bar(x_pos, y_data, align='center', alpha=0.5)
    plt.xticks(x_pos, x_axis)
     
    #legend
    plt.legend(loc=2, ncol=1)

    #vertical x-axis 
    plt.xticks(rotation=90)

    #titles
    plt.title(root_directory, loc='center', fontsize=24, fontweight=0, color='black')
    plt.xlabel(x_axis_title)
    plt.ylabel(y_axis_title)
    plt.tight_layout()

plt.savefig(args.o + '.png')
plt.show()
