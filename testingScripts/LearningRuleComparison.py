import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import copy
import HopfieldNetwork
import PatternManager
from HopfieldUtils import *
import numpy as np
from prettytable import PrettyTable

np.set_printoptions(precision=2)
N = 64
NUMBER_RUNS = 1
MAX_EPOCHS = 500
TEMPERATURE = 1000
DECAY_RATE = np.round((1) * (TEMPERATURE/MAX_EPOCHS),3)
PSEUDOITEMS = 2048

numPatternsByTask = [20]
numPatternsByTask.extend([1 for _ in range(4)])

# HYPERPARAMS ---------------------------------------------------------------------------------------------------------
# Pattern generation params ---------------------------------------------------
mappingFunction = HopfieldNetwork.UpdateRule.ActivationFunction.BipolarHeaviside()
patternManager = PatternManager.SequentialLearningPatternManager(N, mappingFunction)

# Network params---------------------------------------------------------------
energyFunction = HopfieldNetwork.EnergyFunction.BipolarEnergyFunction()
activationFunction = HopfieldNetwork.UpdateRule.ActivationFunction.BipolarHeaviside()
updateRule = HopfieldNetwork.UpdateRule.AsynchronousPermutation(activationFunction, energyFunction)

learning_rules = [

    (HopfieldNetwork.LearningRule.ThermalDelta(maxEpochs=MAX_EPOCHS, temperature=TEMPERATURE, temperatureDecay=DECAY_RATE), "Vanilla"),

    (HopfieldNetwork.LearningRule.RehearsalThermalDelta(maxEpochs=MAX_EPOCHS, temperature=TEMPERATURE, temperatureDecay=DECAY_RATE,
        fracRehearse=1, updateRehearsalStatesFreq="Epoch", rehearseFirstTaskOnly=True), "Rehearsal"),

    (HopfieldNetwork.LearningRule.PseudorehearsalThermalDelta(maxEpochs=MAX_EPOCHS, temperature=TEMPERATURE, temperatureDecay=DECAY_RATE,
        fracRehearse=1, trainUntilStable=False,
        numPseudorehearsalSamples=PSEUDOITEMS, updateRehearsalStatesFreq="Epoch", 
        keepFirstTaskPseudoitems=True, requireUniquePseudoitems=True, 
        rejectLearnedStatesAsPseudoitems=False), "Pseudorehearsal"),

    (HopfieldNetwork.LearningRule.PseudorehearsalThermalDelta(maxEpochs=MAX_EPOCHS, temperature=TEMPERATURE, temperatureDecay=DECAY_RATE,
        fracRehearse=1, trainUntilStable=False,
        numPseudorehearsalSamples=PSEUDOITEMS, updateRehearsalStatesFreq="Epoch", 
        keepFirstTaskPseudoitems=True, requireUniquePseudoitems=True, 
        rejectLearnedStatesAsPseudoitems=True), "Spurious Pseudorehearsal"),




    # (HopfieldNetwork.LearningRule.ElasticWeightConsolidationThermalDelta(
    #     maxEpochs=MAX_EPOCHS, temperature=TEMPERATURE, temperatureDecay=0.0*DECAY_RATE,
    #     ewcTermGenerator=HopfieldNetwork.LearningRule.EWCTerm.WeightDecayTerm, ewcLambda=0.005,
    #     useOnlyFirstEWCTerm=True), "EWC - Omega=1"),
]
# Network noise/error params --------------------------------------------------
allowableLearningStateError = 0.02
inputNoise = None
heteroassociativeNoiseRatio = 0.05


# Array for each learning rule results
results_by_learning_rule = []

for learningRule in learning_rules:
    
    currLearningRuleResults = np.zeros(shape=(len(numPatternsByTask)*MAX_EPOCHS, len(numPatternsByTask)))
    run = 0
    while run < NUMBER_RUNS:
        print(f"{learningRule[1]} RUN: {run+1}/{NUMBER_RUNS}")
        # SETUP ---------------------------------------------------------------------------------------------------------------
        # Create network
        network = HopfieldNetwork.GeneralHopfieldNetwork(
            N=N,
            energyFunction=energyFunction,
            activationFunction=activationFunction,
            updateRule=updateRule,
            learningRule=copy.deepcopy(learningRule[0]),
            allowableLearningStateError=allowableLearningStateError,
            patternManager=patternManager,
            weights=np.random.normal(size=(N,N))
        )

        # numPatternsByTask.extend([1 for i in range(10)])
        tasks = patternManager.createTasks(
            numPatternsByTask=numPatternsByTask
        )

        taskPatternStabilities = np.empty(shape=(0, len(numPatternsByTask)))
        numStableOverEpochs = []
        seenPatterns = []

        # Print network details
        # print(network.getNetworkDescriptionString())
        # print()

        # TRAINING ------------------------------------------------------------------------------------------------------------
        for task in tasks:
            seenPatterns.extend(task.getTaskPatterns())
            
            print(f"{task}")

            # This task has started, note this
            task.startEpoch = network.epochs
            # Learn the patterns
            accuracies, numStable = network.learnPatterns(
                patterns=task.taskPatterns, 
                allTaskPatterns=patternManager.allTaskPatterns, 
                heteroassociativeNoiseRatio=heteroassociativeNoiseRatio, 
                inputNoise=inputNoise
            )

            if isinstance(network.learningRule, HopfieldNetwork.LearningRule.PseudorehearsalDelta) and len(network.learningRule.stableStates) == 0:
                break

            taskPatternStabilities = np.vstack([taskPatternStabilities, accuracies.copy()])
            numStableOverEpochs.extend(numStable)

            print(f"Most Recent Epoch Stable States: {numStable[-1]}")
            print()

        if isinstance(network.learningRule, HopfieldNetwork.LearningRule.PseudorehearsalDelta) and len(network.learningRule.stableStates) == 0:
            print("ERR NO PSEUDOREHEARSAL STATES FOUND\n\n")
            continue

        run += 1 
        currLearningRuleResults += taskPatternStabilities.copy()
    currLearningRuleResults /= NUMBER_RUNS
    results_by_learning_rule.append(currLearningRuleResults[:, 0].copy())

plt.figure(figsize=(12,6))
for i in range(len(results_by_learning_rule)):
    plt.plot(results_by_learning_rule[i], label=learning_rules[i][1])

for i in range(len(numPatternsByTask)):
    plt.axvline(MAX_EPOCHS*i, color=(0, 0, 0, 0.5), linestyle='--', linewidth=0.75)
    plt.text(MAX_EPOCHS*(2*i+1)/2, 0.0, f"Task {i}\n{numPatternsByTask[i]} State{'s' if numPatternsByTask[i]>1 else ''}", horizontalalignment="center")

plt.title(f"Stability of Task 0 by Learning Rule")
plt.xlabel("Epoch")
plt.ylabel("Task 0 Accuracy")
plt.legend(bbox_to_anchor=(1.04, 0.5), loc='center left')
plt.ylim(-0.05, 1.05)
plt.tight_layout()

plt.show()

# PRINT DATA
t = PrettyTable(["Task 0 Stability at end of task"]+[learning_rules[i][1] for i in range(len(learning_rules))])
for i in range(len(numPatternsByTask)):
    t.add_row([f"Task {i}: {numPatternsByTask[i]} State{'s' if numPatternsByTask[i]>1 else ''}"] + [np.round(results_by_learning_rule[lr][MAX_EPOCHS*(i+1)-1], 5) for lr in range(len(learning_rules))])
print(t)