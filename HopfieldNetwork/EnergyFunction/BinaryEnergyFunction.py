from .AbstractEnergyFunction import AbstractEnergyFunction
import numpy as np

class BinaryEnergyFunction(AbstractEnergyFunction):

    def __init__(self):
        """
        Create a new BinaryEnergyFunction that calculates the energy of each unit in a network
        """

    def __call__(self, state:np.ndarray, weights:np.ndarray)->np.ndarray:
        """
        Given a state (a vector of units) and weights, calculate the energy of each unit
        If energy are negative, unit is stable

        Args:
            state (np.ndarray): The vector of units to calculate the energies of. Must be of size N
            weights (np.ndarray): The matrix of weights. Must be of size of N*N.

        Returns:
            np.ndarray: The vector of energies corresponding to the units in the state
        """

        nextState = np.dot(weights, state)
        energies = np.abs(nextState-state)
        return energies

    def __str__(self):
        return "BinaryEnergyFunction"