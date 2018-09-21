import pygame, math, time, random, copy, sys
from pygame.locals import *
from collections import OrderedDict

class timeoutException(Exception):
    pass


WIDTH = 1000
HEIGHT = 600
SCALE = 60

RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
YELLOW = (255,255,224)

pygame.init()

DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.SysFont("Arial", 18)
pygame.display.set_caption("Scenario Sim, v1")

BACKGROUND = pygame.Surface(DISPLAYSURF.get_size())
BACKGROUND = BACKGROUND.convert()
BACKGROUND.fill(BLACK)

# Function for demand
def quintic(t, A, B, C, D, E, F): # The function type that best fits the load profiles
    return A + B*(t) + C*(t**2) + D*(t**3) + E*(t**4) + F*(t**5)
# Function for supply
def bell_func(t, A, K, B):
    return (random.randrange(6,12,1)/12)*A*math.exp(K*(t-B)**2)
    # First param is e, efficiency

global_time_list = [0, 2, 4, 6]

def increment_time():
    global global_time_list
    global_time_list = [x+1 for x in global_time_list]

# def update_agent(agent_obj):
#     if agent_obj.time_zone == 1:
#

class Agent:
    def __init__(self, name, pos, agent_type, hasGeneration):

        self.name = str(name)
        self.agent_type = agent_type
        self.x, self.y = pos
        self.hasGeneration = hasGeneration

        self.supply = 0
        self.demand = 0
        self.net = 0

        self.time_zone = 0
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
        if self.x in range(WIDTH/2) and self.y in range(HEIGHT/2, HEIGHT):
            self.time_zone = 4
            self.t = global_time_list[3]

    @property
    def set_attributes(self):
        if self.agent_type == "Commercial":
            self.color = BLUE
            self.demand = self.demand(116.06, -50.67, 21.861, -2.554, 0.1189, -0.001962)
            if hasGeneration:
                self.supply = self.supply(300, 0.0666666, 13)
                self.net = self.net()

        else:
            self.color = GREEN
            self.demand = self.demand(1.656, -0.9261, 0.3033, -0.03477, 0.001671, -2.846e-5)
            if hasGeneration:
                self.supply = self.supply(3.2, 0.0666666, 13)
                self.net = self.net()


    def demand(self, A, B, C, D, E, F):
        return quintic(self.t, A, B, C, D, E, F)


    def supply(self, A, B, C):
        return bell_func(self.t, A, B, C)


    def net(self):
        return self.supply - self.demand


    def draw(self):
        self.circle_rect = pygame.draw.circle(DISPLAYSURF, self.color, (self.x, self.y), 5)
        pygame.draw.circle(DISPLAYSURF, self.color, (self.x, self.y), 5)
        DISPLAYSURF.blit(FONT.render(self.name, True, GREEN), (self.x, self.y))

    def change_color(self, color):
        self.color = color

    # Pricing psychology will come into play later


# Line has to have with it, congestion and other issues affiliated with it
class Edge:
    def __init__(self, label, start_end): # type(start_end) is tuple
        self.label = str(label)
        self.start, self.end = start_end
        self.length = int(self.get_length())
        self.color = RED

    def draw(self):
        mid_x = (self.start[0] + self.end[0])/2
        mid_y = (self.start[1] + self.end[1])/2
        pygame.draw.line(DISPLAYSURF, self.color, self.start, self.end)
        DISPLAYSURF.blit(FONT.render(str(self.length), True, WHITE), (mid_x, mid_y))

    def change_color(self, color):
        self.color = color

    def get_length(self):
        x_1, y_1 = self.start
        x_2, y_2 = self.end
        return "%.0f" % math.hypot(x_1 - x_2, y_1 - y_2)


# MARK: Network Topology Requirements
agent_dict = {}
edge_dict = {}
seller_dict = {}
buyer_dict = {}
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
            16 : (926,371)
}
edges_list = """
1:2 1:3 2:4 1:4 3:4 3:5 2:6 6:1 4:5 7:2 7:0 7:11 13:10
12:1 1:10 3:13 13:9 13:14 9:14 13:15 8:16 5:8 16:15 0:2
"""
edges_list = [x.split(':') for x in edges_list.split()]

for agent in agent_pos: # Creating the agents
    agent_dict[agent] = Agent(agent, agent_pos[agent], random.choice(["Commercial", "Residential"]),random.getrandbits(1))


if __name__ == "__main__":
    clock = pygame.time.Clock()

    while 1:
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        for agent in agent_dict:
            print "Agent Name", agent_dict[agent].name, " Agent type:", agent_dict[agent].agent_type, " has generation?", agent_dict[agent].net, "In time", agent_dict[agent].time_zone, "Currently in year", agent_dict[agent].t

        increment_time() # Call this when we are incrementing time and updating

        print "\n##########################--INCREMENT--###############################\n"

        clock.tick(60)

