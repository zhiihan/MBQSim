from graph_state import GraphState
from collections import Counter
import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt5agg")

class Grid(GraphState):
    def __init__(self, width, height, length):
        self.height = height
        self.width = width
        self.length = length
        super().__init__(width*height*length)
        self.edges = []
        self.removed = []

        for j in range(self.height):
            for i in range(self.width-1):
                self.edges.append((i+j*self.width, (i+1)+j*self.width))
        for j in range(self.height-1):
            for i in range(self.width):
                self.edges.append((i+j*self.width, i+(j+1)*self.width))
        
        for i in range(self.height*self.width):
            self.h(i)
        
        for e in self.edges:
            self.add_edge(*e)

        self.G = self.to_networkx()
        self.get_node_coords()

    def get_node_coords(self):
        """
        Get node coordinates.
        """
        self.node_coords = {}

        for i in range(self.height):
            for j in range(self.width):
                for k in range(self.length):
                    self.node_coords.update({
                        str(i*self.width*self.length + j*self.length + k) : np.array([i, j, k])
                    })      
        

    def damage_grid(self, p):
        # p is the probability of losing a qubit

        for i in range(self.height*self.width):
            if random.random() < p:
                self.measure(i)
                self.removed.append(i)

    def draw(self):
        fig, ax = plt.subplots()
        fig.canvas.mpl_connect('button_press_event', self.onClick)
        
        self.G = self.to_networkx()
        self.pos_nodes = {i: ((i%self.width), -(i//self.width)) for i in self.G.nodes()}

        for i in self.removed:
            self.G.remove_node(i)

        nx.draw(self.G, self.pos_nodes, with_labels=True)

        pos_attrs = {}
        for node, coords in self.pos_nodes.items():
            pos_attrs[node] = (coords[0], coords[1] + 0.08)

        node_attrs = nx.get_node_attributes(self.G, 'vop')
        custom_node_attrs = {}
        for node, attr in node_attrs.items():
            custom_node_attrs[node] = attr

        nx.draw_networkx_labels(self.G, pos_attrs, labels=custom_node_attrs)
        plt.show()

    def onClick(self, event):
        (x, y) = (event.xdata, event.ydata)

        for i in self.pos_nodes:
            distance = pow(x-self.pos_nodes[i][0],2)+pow(y-self.pos_nodes[i][1],2)
            if distance < 0.1 and i not in self.removed:
                self.removed.append(i)
                print(i, self.removed) 
                if event.button == 1:
                    print('lmb', x, y)
                    self.measure(i)
                if event.button == 3:
                    print('rmb', x, y)
                    self.measure(i, basis='Y')
        self.refreshGraph()

    def refreshGraph(self):
        plt.clf()
        self.draw()

    def adjaencyMatrix(self):
        return nx.to_numpy_array(self.to_networkx())
