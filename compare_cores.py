import utils
import argparse
import os
import matplotlib.pyplot as plt

def my_autopct(values):
    def my_autopct(pct):
        if pct < 1:
            return ''
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.1f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

########################
#Command-line arguments#
########################

parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--cp1", required=True, type=str, help="path to the file containing the first core file to compare (core path 1)")
parser.add_argument("--cp2", required=True, type=str, help="path to the file containing the second core file to compare (core path 2)")
parser.add_argument("--o", default="repartition", type=str, help="file name for the output png")
args = parser.parse_args()

#########################################
#Getting data to plot (reuse-core sizes)#
#########################################


print ("###############################")
print ("getting reuse-cores and counting identical members...")

core1 = utils.get_csv_rows(args.cp1)
core2 = utils.get_csv_rows(args.cp2)
cores_intersection = [member for member in core1 if member in core2] 

only_core1_size = len(core1) - len(cores_intersection)
only_core2_size = len(core2) - len(cores_intersection)
intersection_size = len(cores_intersection)
print ("There are " + str(only_core1_size) + " members which are only in first reuse_core")
print ("There are " + str(only_core2_size) + " members which are only in second reuse_core")
print ("There are " + str(intersection_size) + " members which are in the two reuse-cores")

######
#Plot#
######

# style
plt.style.use('seaborn-darkgrid')

labels = ["First core", "Second core", "Intersection"]
values = [only_core1_size, only_core2_size, intersection_size]
colors = ["red", "blue", "green"]
patches, texts , autotexts = plt.pie(values, colors=colors, autopct=my_autopct(values), startangle=90)
plt.legend(patches, labels, loc="best")
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title("Comparison of two reuse cores", loc='center', fontsize=16, fontweight=0, color='black')
plt.tight_layout()

plt.savefig(args.o + '.png')
plt.show()
