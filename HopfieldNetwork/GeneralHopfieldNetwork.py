from typing import List, Tuple, Union
from .AbstractHopfieldNetwork import AbstractHopfieldNetwork
from .UpdateRule.AbstractUpdateRule import AbstractUpdateRule
from .EnergyFunction.AbstractEnergyFunction import AbstractEnergyFunction
from .UpdateRule.ActivationFunction.AbstractActivationFunction import AbstractActivationFunction
from .LearningRule.AbstractLearningRule import AbstractLearningRule
import numpy as np

class RelaxationException(Exception):
    pass

class GeneralHopfieldNetwork(AbstractHopfieldNetwork):

    def __init__(self, 
                N:int,
                energyFunction:AbstractEnergyFunction,
                activationFunction:AbstractActivationFunction, 
                updateRule:AbstractUpdateRule,
                learningRule:AbstractLearningRule, 
                allowableLearningStateError:np.float64=0,
                patternManager=None,
                weights:np.ndarray=None,
                selfConnections:bool=False):
        """
        Create a new General Hopfield network with N units.
        All options are available in the constructor.
        
        If weights is supplied, the network weights are set to the supplied weights.

        Args:
            N (int): The size of the network, how many units to have.
            weights (np.ndarray, optional): The weights of the network, if supplied. Intended to be used to recreate a network for testing.
                If supplied, must be a 2-D matrix of float64 with size N*N. If None, random weights are created uniformly around 0.
                Defaults to None.
            activationFunction (AbstractActivationFunction): The activation function to use with this network. 
                Must implement HopfieldNetwork.ActivationFunction.AbstractActivationFunction
                The given functions in HopfieldNetwork.ActivationFunction do this.
            updateRule (AbstractUpdateRule): The update rule for this network.
                Must implement HopfieldNetwork.UpdateRule.AbstractUpdateRule
                The given methods in HopfieldNetwork.UpdateRule do this.
            learningRule (AbstractLearningRule): The learning rule for this network.
                Must implement HopfieldNetwork.LearningRule.AbstractUpdateRule
                The given methods in HopfieldNetwork.LearningRule do this.
            allowableLearningStateError (np.float64, optional): The allowable error (as a ratio of all units) for a pattern to be stable
                Implemented as a check of Hamming distance against the intended pattern during learning.
                If 0 (default), the pattern must be exactly the same.
            patternManager : The pattern manager that creates the patterns for this network. Optional, Defaults to None
            weights (np.ndarray, optional): The weights of this network. Must be of dimension N*N.
                Used for reproducibility. Defaults to None.
            selfConnections (bool, optional): Determines if self connections are allowed or if they are zeroed out during learning
                Defaults to False. (No self connections)

        Raises:
            ValueError: If the given weight matrix is not N*N and not None.
        """

        super().__init__(
            N=N,
            energyFunction=energyFunction,
            activationFunction=activationFunction,
            updateRule=updateRule,
            learningRule=learningRule,
            allowableLearningStateError=allowableLearningStateError,
            weights=weights,
            selfConnections=selfConnections,
            patternManager=patternManager
        )

        self.networkName:str = "GeneralHopfieldNetwork"

    def __str__(self):
        return f"Hopfield Network: {self.networkName}"
    
    def setState(self, state:np.ndarray):
        """
        Set the state of this network.

        Given state must be a float64 vector of size N. Any other type will raise a ValueError.

        Args:
            state (np.ndarray): The state to set this network to.

        Raises:
            ValueError: If the given state is not a float64 vector of size N.
        """

        super().setState(state.copy())

    def learnPatterns(self, patterns:List[np.ndarray], allTaskPatterns:List[List[np.ndarray]]=None, 
        heteroassociativeNoiseRatio:np.float64=0, inputNoise:str=None)->Union[None, Tuple[List[List[np.float64]], List[int]]]:
        """
        Learn a set of patterns given. This method will use the learning rule given at construction to learn the patterns.
        The patterns are given as a list of np.ndarrays which must each be a vector of size N.

        Args:
            patterns (List[np.ndarray]): The patterns to learn. Each np.ndarray must be a float64 vector of length N (to match the state)
            allTaskPatterns (List[List[np.ndarray]] or None, optional): If given, will track the task pattern stability by epoch during training.
                Passed straight to measureTaskPatternAccuracy. Defaults to None.
            heteroassociativeNoiseRatio (np.float64, optional): The fraction of units to add a noise term to before calculating error.
                Must be between 0 and 1. Defaults to 0.
            inputNoise (str or None, optional): String on whether to apply input noise to the units before activation
                - "Absolute": Apply absolute noise to the state, a Gaussian of mean 0 std 1
                - "Relative": Apply relative noise to the state, a Gaussian of mean and std determined by the state vector
                - None: No noise. Default

        Returns: None or List[Tuple[List[np.float64], int]]]
            If allTaskPatterns is None, returns None
            If allTaskPatterns is present, returns a list over epochs of tuples. Tuples are of form (list of task accuracies, num stable learned patterns overall)
        """

        return super().learnPatterns(patterns.copy(), allTaskPatterns, heteroassociativeNoiseRatio, inputNoise)