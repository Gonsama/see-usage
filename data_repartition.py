import utils
import argparse
import os
import matplotlib.pyplot as plt
import numpy as np

########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--lp", required=True, type=str, help="path to the repertory of the library (groupid + artifactid)")
parser.add_argument("--o", default="repartition", type=str, help="file name for the output png")
args = parser.parse_args()

#########################################
#Getting data to plot (reuse-core sizes)#
#########################################

root_directory = args.lp

#getting all versions (path, timestamp) tuple
versions_tuple= [(x[0],utils.get_timestamp(x[0])) for x in os.walk(args.lp) if x[0] != root_directory]

#sort list so that versions are in ascending order
versions_tuple = sorted(versions_tuple, key=lambda tup: tup[1])

#visit subdirectories one by one to compute the wanted values (number of rows for each version)
y_data = []
for path,t in versions_tuple:
    nb_rows = utils.get_csv_rows_nb(path + "/library-usage.csv")
    y_data.append(nb_rows)

versions = [path.split("/")[2] for path,t in versions_tuple]
#space between versions will be equal
#split path to get only versions
x_axis = versions

x_axis_title = "library version"
y_axis_title = "number of usages"

######
#Plot#
######

 
# style
plt.style.use('seaborn-darkgrid')

#bar chart
x_pos = np.arange(len(x_axis))
plt.bar(x_pos, y_data, align='center', alpha=0.5)
plt.xticks(x_pos, x_axis)
 
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
