import math, time, random, copy, sys, decimal
from collections import OrderedDict

class timeoutException(Exception):
    pass

def find_path(start_node, end_node):
    global network_graph, Lead_Vec, agent_dict, timeoutException

    prev_child = start_node
    current_node = start_node
    path = []
    visited_nodes = []
    to_delete_nodes = []

    path.append(start_node)
    visited_nodes.append(start_node)

    if start_node not in network_graph or end_node not in network_graph:
        return "Can't find"

    while current_node != end_node:
        lead_lengths = {}

        if len(network_graph[current_node]) > 0:
            # --> find leadvec distances from each child node
            for c_node in network_graph[current_node]:
                if c_node not in visited_nodes:
                    lead_lengths[c_node] = Lead_Vec(agent_dict[c_node], agent_dict[end_node]).length()

            try:
                new_child = min(lead_lengths, key=lead_lengths.get)
            except:
                new_child = prev_child

            # --> If already visited
            start_time = time.time()
            while new_child in visited_nodes:
                # --> Time out exception
                if time.time() - start_time > 2:
                    raise timeoutException


                lead_lengths.clear()
                visited_nodes.append(new_child)
                to_delete_nodes.append(current_node)

                for c_node in network_graph[new_child]:
                    if c_node not in visited_nodes:
                        lead_lengths[c_node] = Lead_Vec(agent_dict[c_node], agent_dict[end_node]).length()


                if len(lead_lengths) > 0:
                    new_child = min(lead_lengths, key=lead_lengths.get)
                else:
                    new_child = prev_child


            visited_nodes.append(new_child)
            path.append(new_child)
            path = list(OrderedDict.fromkeys(path))

            prev_child = current_node
            current_node = new_child

        else:
            visited_nodes.append(current_node)
            current_node = prev_child

    # --> Filter the list to get rid of all corresponding to_delete_nodes
    return [x for x in path if x not in to_delete_nodes]
def determine_edges_c(path):
    # --> Finds the edges for the node list given
    connected_edges = []
    for x in range(1, len(path)):
        prev = str(path[x - 1])
        second = str(path[x])
        pair = (prev, second)
        r_pair = (second, prev)
        if pair != r_pair:
            connected_edges.append(pair)
            connected_edges.append(r_pair)
    return connected_edges
def path_distance(edge_list):
    global edge_dict
    distance_list = []
    for element in edge_list:
        if element in edge_dict:
            distance_list.append(edge_dict[element].length)
    return sum(distance_list)
def find_shortest_path(start_node, end_node):
    try:
        path = find_path(start_node, end_node)
        r_path = find_path(end_node, start_node)
        dis = path_distance(determine_edges_c(path))
        r_dis = path_distance(determine_edges_c(r_path))
        if r_dis < dis:
            return r_path[::-1] # We reverse the path because it's been backward checked
        return path
    except timeoutException:
        r_path = find_path(end_node, start_node)
        return r_path[::-1]
