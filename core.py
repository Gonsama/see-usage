import networkx as nx
from networkx.algorithms import bipartite
import csv
import sys
import argparse
import os
import utils

#this function visits the graph to compute the satisfaction percent of the clients at the graph's current state (when hiding api members)
def get_satisfaction_percent(G, G_top, nb_of_clients):
    """returns the satisfaction percent of the clients with actual graph"""
    unsatisfied_clients = 0    
    for n in G_top:
        neighbor_api_members = G.neighbors(n)
        for m in neighbor_api_members:
            #print n, m, G.edges[n,m]['hidden']
            if G.edges[n,m]['hidden'] == 1:
                unsatisfied_clients += 1
                break

    satisfaction_percent = (nb_of_clients - unsatisfied_clients) / float(nb_of_clients) * 100

    return satisfaction_percent

def sort_by_degree(list_of_nodes, G):
    """sort list of nodes l by degree of nodes in graph G"""
    tuples_list = []
    for node in list_of_nodes:
        degree = G.degree(node)
        tuples_list.append((node, degree))

    #sort list so that degrees are in ascending order
    tuples_list_sorted = sorted(tuples_list, key=lambda tup: tup[1])    
    sorted_list = [n for n,d in tuples_list_sorted]
    return sorted_list    

#command-line arguments
parser = argparse.ArgumentParser(description='Welcome!')
parser.add_argument("--path", required=True, type=str, help="path to the repertory of a certain library or of multiple libraries")
parser.add_argument("--percent", default=50, type=int, help="reuse-core percentage wanted")
args = parser.parse_args()

#getting path to subdirectories containing a library-usage.csv file
root_directory = args.path
pattern = "*library-usage.csv"
chosen_libraries_path = utils.get_paths_containing_pattern(root_directory, pattern)


for path in chosen_libraries_path:

    print ("###############################################")
    print ("reading " + path + "/library-usage.csv" + "...")

    with open(path + "/library-usage.csv", 'r') as f:
      reader = csv.reader(f)
      csv_data = list(reader)


    print ("Computing reuse-core...")

    reuse_core_percentage = int(args.percent)

    #first row must be deleted because it represents the column names
    csv_data.pop(0)
    
    #not necessary to compute reuse-core for empty csv file, so empty file is created for the reuse-core too   
    if len(csv_data) < 1:
        f = open(path + "/reuse-core-" + str(reuse_core_percentage) + ".csv", "w")
        myFile = csv.writer(f, lineterminator = '\n')
        myFile.writerow(["reuse-core-member"])
        f.close()
        continue
    
    clients = []
    api_members = []
    for x in csv_data:
        clients.append(x[0] + ":" + x[1] + ":" + x[2])
        api_members.append(x[3] + ":" + x[4] + ":" + x[5])

    print ("number of edges:" + str(len(clients)))
    clients_nodes = set(clients)
    api_members_nodes = set(api_members)
    print ("number of unique clients:" + str(len(clients_nodes)))
    print ("number of unique apimembers:" + str(len(api_members_nodes)))

    #creating and filling bipartite graph (clients <--> api_members)
    B = nx.Graph() 
    B.add_nodes_from(clients_nodes, bipartite=0)
    B.add_nodes_from(api_members_nodes, bipartite=1)
    for i in range(len(clients)) :
        #edges initialized with hidden = 0, meaning edge is not hidden
        B.add_edge(clients[i], api_members[i], hidden=0)

    nb_of_clients = len(clients_nodes)
    reuse_core = api_members_nodes.copy()

    #top and bottom represents the two sets of the bipartite graph
    #the order of the bottom is very important because the first elements are being considered first (to be removed)
    #we chose to sort by degree of nodes in ascending order (list is first sorted by strings so that nodes with same degree will be in the same order too)
    B_top = clients_nodes
    B_bottom = sort_by_degree(sorted(api_members_nodes), B)

    #hiding edges going to 1 api_member at a time until satisfaction percent is equal or greater than reuse_core_percentage
    for n in B_bottom:
        neighbor_clients = B.neighbors(n)
        for c in neighbor_clients:
            B.edges[c,n]['hidden'] = 1
        
        #reversing the process of hiding if the satisfaction percent is too low
        #as it is an iterator, we have to call neigbors again
        neighbor_clients = B.neighbors(n)
        if get_satisfaction_percent(B, B_top, nb_of_clients) < reuse_core_percentage:
            for c in neighbor_clients:
                B.edges[c,n]['hidden'] = 0
        else:
            reuse_core.remove(n)

    satisfaction_percent = get_satisfaction_percent(B, B_top, nb_of_clients)

    print ("The number of clients using the library: " + str(nb_of_clients))
    print ("Satisfaction percent: " + str(satisfaction_percent))
    print ("The number of clients satisfied with reuse-core: " + str(satisfaction_percent * nb_of_clients / 100))
    print ("size of all api_members: " + str(len(api_members_nodes)))
    print ("size of reuse-core: " + str(len(reuse_core)))

    #writing reuse-core elements in csv file
    f = open(path + "/reuse-core-" + str(reuse_core_percentage) + ".csv", "w")
    myFile = csv.writer(f, lineterminator = '\n')
    myFile.writerow(["reuse-core-member"])
    for x in reuse_core:
        myFile.writerow([x])
    f.close()
    print ("###############################################")
