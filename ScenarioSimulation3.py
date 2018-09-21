import pygame, math, time, random, copy, sys, decimal
from pygame.locals import *
from collections import OrderedDict
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy

class timeoutException(Exception):
    pass

# MARK: Matplotlib and txt file

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
            17 : (100, 500),
            18 : (20, 490),
            19 : (30, 540),
            20 : (900, 540),
            21 : (900, 420)
}
edges_list = """
1:2 1:3 2:4 1:4 3:4 3:5 2:6 6:1 4:5 7:2 7:0 7:11 13:10
12:1 1:10 3:13 13:9 13:14 9:14 13:15 8:16 5:8 16:15 0:2 17:3
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

