import numpy as np
import random
from scipy.special import expit as activation_function
from scipy.stats import truncnorm

def truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

class NeuralNetwork:
           
    def __init__(self, 
                 no_of_in_nodes, 
                 no_of_out_nodes, 
                 no_of_hidden_nodes):
        self.no_of_in_nodes = no_of_in_nodes
        self.no_of_out_nodes = no_of_out_nodes
        self.no_of_hidden_nodes = no_of_hidden_nodes
#        self.create_weight_matrices()
        self.randomize()
        self.set_fixed()

    def set_fixed(self):
        self.weights_in_hidden = [
                [0.7, 0.7],
                [0.7, 0.7],
                [0.7, 0.7],
                [0.7, 0.7],
                ]
        self.weights_hidden_out = [
                [0.7, 0.7, 0.7, 0.7],
                [0.7, 0.7, 0.7, 0.7],
                ]

    def randomize(self):
        self.weights_in_hidden = []
        self.weights_hidden_out = []
        for i in range(self.no_of_hidden_nodes):
            wih = []
            for j in range(self.no_of_in_nodes):
                wih.append(random.random())
            self.weights_in_hidden.append(wih)

        for i in range(self.no_of_out_nodes):
            who = []
            for j in range(self.no_of_hidden_nodes):
                who.append(random.random())
            self.weights_hidden_out.append(who)

        
    def create_weight_matrices(self):
        """ A method to initialize the weight matrices of the neural network"""
        rad = 1 / np.sqrt(self.no_of_in_nodes)
        X = truncated_normal(mean=0, sd=1, low=-rad, upp=rad)
        self.weights_in_hidden = X.rvs((self.no_of_hidden_nodes, self.no_of_in_nodes))

        rad = 1 / np.sqrt(self.no_of_hidden_nodes)
        X = truncated_normal(mean=0, sd=1, low=-rad, upp=rad)
        self.weights_hidden_out = X.rvs((self.no_of_out_nodes, self.no_of_hidden_nodes))
    
    
    def run(self, input_vector):
        """
        running the network with an input vector input_vector. 
        input_vector can be tuple, list or ndarray
        """
        
        # turning the input vector into a column vector
        input_vector = np.array(input_vector, ndmin=2).T
        output_vector = np.dot(self.weights_in_hidden, input_vector)
        output_vector = activation_function(output_vector)
        
        output_vector = np.dot(self.weights_hidden_out, output_vector)
        output_vector = activation_function(output_vector)
    
        return output_vector

