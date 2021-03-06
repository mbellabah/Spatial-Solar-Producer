import pygame, math, time, random, copy, sys, decimal
from pygame.locals import *
from collections import OrderedDict
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy


class timeoutException(Exception):
    pass


# MARK: PyGame initialization
WIDTH = 1000
HEIGHT = 600
SCALE = 60

RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
YELLOW = (255,255,224)

global_time_list = [0, 4, 7, 18]
global_net_power = 0

pygame.init()

DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.SysFont("Arial", 15)
FONT_2 = pygame.font.SysFont("Arial", 10)
pygame.display.set_caption("Scenario Sim, v1")

BACKGROUND = pygame.Surface(DISPLAYSURF.get_size())
BACKGROUND = BACKGROUND.convert()
BACKGROUND.fill(BLACK)

# MARK: Debug functions
def print_debug(agent_obj):
    print "Type: {}, Zone: {}, Has Generation: {}".format(agent_obj.agent_type, agent_obj.time_zone, agent_obj.hasGeneration)

# MARK: Functions regarding production and finance
def quintic(t, A, B, C, D, E, F): # The function type that best fits the load profiles
    return (float(decimal.Decimal(random.randrange(5, 12))/10))*(A + B*(t) + C*(t**2) + D*(t**3) + E*(t**4) + F*(t**5))
def bell_func(t, A, K, B):
    return (float(decimal.Decimal(random.randrange(9, 15))/10))*A*math.exp(-K*(t-B)**2)
    # First param is e, efficiency
def increment_time():
    global global_time_list
    def update_value(x):
        if x < 24:
            return x+1
        else:
            return 0

    global_time_list = [update_value(x)for x in global_time_list]
def update_agent(agent_obj):
    global global_time_list
    t_z = agent_obj.time_zone
    if t_z == 1:
        agent_obj.t = global_time_list[0]
    if t_z == 2:
        agent_obj.t = global_time_list[1]
    if t_z == 3:
        agent_obj.t = global_time_list[2]
    if t_z == 4:
        agent_obj.t = global_time_list[3]



# MARK: Agent Classes
class Commercial_Agent:
    def __init__(self, name, pos, hasGeneration):
        self.name = str(name)
        self.circle_rect = None

        self.color = BLUE
        self.agent_type = "Commercial"
        self.x, self.y = pos
        self.hasGeneration = hasGeneration

        self.time_zone = 1
        self.t = 0

        if self.x in range(0, WIDTH/2) and self.y in range(0, HEIGHT/2):
            self.time_zone = 1
            self.t = global_time_list[0]
        if self.x in range(WIDTH/2, WIDTH) and self.y in range(0, HEIGHT/2):
            self.time_zone = 2
            self.t = global_time_list[1]
        if self.x in range(0, WIDTH/2) and self.y in range(HEIGHT/2, HEIGHT):
            self.time_zone = 3
            self.t = global_time_list[2]
        if self.x in range(WIDTH/2, WIDTH) and self.y in range(HEIGHT/2, HEIGHT):
            self.time_zone = 4
            self.t = global_time_list[3]

    @property
    def demand(self):
        return quintic(self.t, 116.06, -50.67, 21.861, -2.554, 0.1189, -0.001962)

    @property
    def supply(self):
        if self.hasGeneration:
            return bell_func(self.t, 300, 0.0666666, 13)
        else:
            return 0

    @property
    def net(self):
        return self.supply - self.demand

    def draw(self):
        self.circle_rect = pygame.draw.circle(DISPLAYSURF, self.color, (self.x, self.y), 5)
        pygame.draw.circle(DISPLAYSURF, self.color, (self.x, self.y), 5)
        DISPLAYSURF.blit(FONT.render((self.name + " ," + str(self.net)[0:6]), True, WHITE),(self.x, self.y))

    def change_color(self, color):
        self.color = color
class Residential_Agent:
    def __init__(self, name, pos, hasGeneration):
        self.name = str(name)
        self.circle_rect = None

        self.color = GREEN
        self.agent_type = "Residential"
        self.x, self.y = pos
        self.hasGeneration = hasGeneration

        self.time_zone = 1
        self.t = 0

        if self.x in range(0, WIDTH / 2) and self.y in range(0, HEIGHT / 2):
            self.time_zone = 1
            self.t = global_time_list[0]
        if self.x in range(WIDTH / 2, WIDTH) and self.y in range(0, HEIGHT / 2):
            self.time_zone = 2
            self.t = global_time_list[1]
        if self.x in range(0, WIDTH / 2) and self.y in range(HEIGHT / 2, HEIGHT):
            self.time_zone = 3
            self.t = global_time_list[2]
        if self.x in range(WIDTH / 2, WIDTH) and self.y in range(HEIGHT / 2, HEIGHT):
            self.time_zone = 4
            self.t = global_time_list[3]

    @property
    def demand(self):
        return quintic(self.t, 1.656, -0.9261, 0.3033, -0.03477, 0.001671, -2.846e-5)

    @property
    def supply(self):
        if self.hasGeneration:
            return bell_func(self.t, 3.2, 0.0666666, 13)
        else:
            return 0

    @property
    def net(self):
        return self.supply - self.demand


    def draw(self):
        self.circle_rect = pygame.draw.circle(DISPLAYSURF, self.color, (self.x, self.y), 5)
        pygame.draw.circle(DISPLAYSURF, self.color, (self.x, self.y), 5)
        DISPLAYSURF.blit(FONT.render((self.name + " ," + str(self.net)[0:6]), True, WHITE), (self.x, self.y))

    def change_color(self, color):
        self.color = color
class Edge:
    def __init__(self, label, start_end):
        self.label = str(label)
        self.start, self.end = start_end
        self.length = int(self.get_length())
        self.color = RED
        #self.max_capacity = 0
        # CONGESTION OF THE LINE (Line Capacity) --> Combines to form a weighting

    def draw(self):
        mid_x = (self.start[0] + self.end[0])/2
        mid_y = (self.start[1] + self.end[1])/2
        pygame.draw.line(DISPLAYSURF, self.color, self.start, self.end)
        DISPLAYSURF.blit(FONT_2.render(str(self.length), True, WHITE), (mid_x, mid_y))
    def get_length(self):
        x_1, y_1 = self.start
        x_2, y_2 = self.end
        return "%.0f" % math.hypot(x_1 - x_2, y_1 - y_2)
class Lead_Vec:
    def __init__(self, s_node, e_node):
        self.s_node = s_node
        self.e_node = e_node

    def draw(self):
        pygame.draw.line(DISPLAYSURF, BLUE, (self.s_node.x, self.s_node.y), (self.e_node.x, self.e_node.y), 5)

    def length(self):
        return Edge("Lead_Vec", ((self.s_node.x, self.s_node.y), (self.e_node.x, self.e_node.y))).length


# MARK: Network Topology
edge_dict = {}
agent_dict = {}
network_graph = {}

agent_pos = {0 : (10,10),
            1 : (200,200),
            2 : (100,100),
            3 : (350,80),
            4 : (190,30),
            5 : (300,20),
            6 : (130,300),
            7 : (50,200),
            8 : (958,54),
            9 : (298,434),
            10 : (340,275),
            11 : (57,264),
            12 : (354,332),
            13 : (525,232),
            14 : (601,526),
            15 : (749,442),
            16 : (926,371),
            17 : (100, 500)
}
edges_list = """
1:2 1:3 2:4 1:4 3:4 3:5 2:6 6:1 4:5 7:2 7:0 7:11 13:10
12:1 1:10 3:13 13:9 13:14 9:14 13:15 8:16 5:8 16:15 0:2 17:9 17:6
"""
edges_list = [x.split(':') for x in edges_list.split()]
for agent in agent_pos: # Creating the agents
    choice_type = random.choice(["Commercial", "Residential"])
    if choice_type == "Commercial":
        agent_dict[agent] = Commercial_Agent(agent, agent_pos[agent], 1)
    else:
        agent_dict[agent] = Residential_Agent(agent, agent_pos[agent], random.getrandbits(1))

    print print_debug(agent_dict[agent])
for edge_el in edges_list:
    edge_el = tuple(edge_el)
    edge_dict[edge_el] = Edge(edge_el, (agent_pos[int(edge_el[0])], agent_pos[int(edge_el[1])]))

# --> Build the actual network graph
for node_name in agent_dict:
    network_graph[node_name] = []
for edge_name in edges_list:
    edge_f = int(edge_name[0])
    edge_i = int(edge_name[1])
    network_graph.setdefault(edge_i, list()).append(edge_f)
    network_graph[edge_f].append(edge_i)

# MARK: Functions concerning network navigation

def find_path(start_node, end_node):
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


# MARK: Functions concerning matching the network

def match_for_buyer(buyer_node, seller_dict):
    # # --> Returns a dictionary of the matches of the buyer node
    # match_dict = {}
    # b_name = buyer_node.name
    # for seller in seller_dict:
    #     pair_name = b_name + "," + seller_dict[seller].name
    pass


# MARK: Functions that alter the GUI
def draw_all_nodes():
    for el in agent_pos:
        agent_dict[el].draw()
def draw_indv_edge(edge):
    edge.draw()


# MARK: Actual Opening of the GUI

count = 0

if __name__ == "__main__":
    clock = pygame.time.Clock()
    DISPLAYSURF.blit(BACKGROUND, (0,0))


    while 1:
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                open('example.txt','w').close()
                pygame.quit()
                sys.exit()

        # Increment time and update the agents
        increment_time()
        for agent in agent_dict:
            update_agent(agent_dict[agent])
            global_net_power += agent_dict[agent].net


        # Updates the screen
        DISPLAYSURF.blit(BACKGROUND, (0, 0))
        DISPLAYSURF.blit(FONT.render("Hour: " + str(global_time_list), True, WHITE), (0,HEIGHT-30))
        DISPLAYSURF.blit(FONT.render("Global net power: " + str(global_net_power), True, WHITE), (120, HEIGHT-30))
        draw_all_nodes()
        for element in edges_list:
            element = tuple(element)
            edge_dict[element].draw()


        if count < 72:
            open('example.txt', 'a').write("{},{}\n".format(count, global_net_power))
            count += 1
        else:
            open('example.txt', 'w').close()
            count = 0


        global_net_power = 0

        pygame.display.update()
        clock.tick(60)
        time.sleep(0.25)

