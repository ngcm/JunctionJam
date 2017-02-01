#!/usr/bin/env python
"""
@file    actuatedControl.py
@author  Craig Rafter
@date    15/08/2016

class for fixed time signal control

"""
import signalControl, readJunctionData, traci
import numpy as np
from collections import defaultdict


class actuatedControl(signalControl.signalControl):
    def __init__(self, junctionData, minGreenTime=10, maxGreenTime=60, extendTime=1):
        super(actuatedControl, self).__init__()
        self.junctionData = junctionData
        self.firstCalled = self.getCurrentSUMOtime()
        self.lastCalled = self.getCurrentSUMOtime()
        self.lastStageIndex = 0
        traci.trafficlights.setRedYellowGreenState(self.junctionData.id, 
            self.junctionData.stages[self.lastStageIndex].controlString)
        
        self.minGreenTime = minGreenTime
        self.maxGreenTime = maxGreenTime
        self.extendTimePerStep = 0.001*extendTime*traci.simulation.getDeltaT()
        self.stageTime = 0.0
        self.controlledLanes = traci.trafficlights.getControlledLanes(self.junctionData.id)
        self.laneInductors = self._getLaneInductors()

    def process(self):
        # Get actuation information and make actuation decision
        activeLanes = self._getActiveLanes()
        meanDetectTimePerLane = np.zeros(len(activeLanes))
        for i, lane in enumerate(activeLanes):
            detectTimes = []
            for loop in self.laneInductors[lane]:
                detectTimes.append(traci.inductionloop.getTimeSinceDetection(loop))
            meanDetectTimePerLane[i] = np.mean(detectTimes)
        
        # Set adaptive time limit
        if np.any(meanDetectTimePerLane < 2):
            extend = self.extendTimePerStep
        else:
            extend = 0.0

        self.stageTime = max(self.stageTime, self.minGreenTime) + extend
        self.stageTime = min(self.stageTime, self.maxGreenTime)
        
        # Process light state
        if self.transitionObject.active:
            # If the transition object is active i.e. processing a transition
            pass
        elif (self.getCurrentSUMOtime() - self.firstCalled) < (self.junctionData.offset*1000):
            # Process offset first
            pass
        elif (self.getCurrentSUMOtime() - self.lastCalled) < self.stageTime*1000:
            # Before the period of the next stage
            pass
        else:
            # Not active, not in offset, stage not finished
            if len(self.junctionData.stages) != (self.lastStageIndex)+1:
                # Loop from final stage to first stage
                self.transitionObject.newTransition(
                    self.junctionData.id, 
                    self.junctionData.stages[self.lastStageIndex].controlString,
                    self.junctionData.stages[self.lastStageIndex+1].controlString)
                self.lastStageIndex += 1
            else:
                # Proceed to next stage
                self.transitionObject.newTransition(
                    self.junctionData.id, 
                    self.junctionData.stages[self.lastStageIndex].controlString,
                    self.junctionData.stages[0].controlString)
                self.lastStageIndex = 0

            # print(0.001*(self.getCurrentSUMOtime() - self.lastCalled))
            self.lastCalled = self.getCurrentSUMOtime()
            self.stageTime = 0.0
                
        super(actuatedControl, self).process()


    def _getActiveLanes(self):
        # Get the current control string to find the green lights
        stageCtrlString = self.junctionData.stages[self.lastStageIndex].controlString
        activeLanes = []
        for i, letter in enumerate(stageCtrlString):
            if letter == 'G':
                activeLanes.append(self.controlledLanes[i])
        # Get a list of the unique 
        activeLanes = list(np.unique(np.array(activeLanes)))
        return activeLanes


    def _getLaneInductors(self):
        laneInductors = defaultdict(list)

        for loop in traci.inductionloop.getIDList():
            loopLane = traci.inductionloop.getLaneID(loop)
            if loopLane in self.controlledLanes:
                laneInductors[loopLane].append(loop)
            
        return laneInductors
