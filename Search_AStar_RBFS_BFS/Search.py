#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 19:59:07 2019

@author: shaivalshah
"""
import time
from heapq import heappush, heappop
import sys

algo = sys.argv[1]
file_path = sys.argv[2]


class Node:
    """
    Each object of node class represents the state of the globe including path cost, heuristics and total cost.
    Also the parent node reference and step taken from the parent node is stored.
    
    #Arguments
        state: 2D matrix of 30X2 shape, represent state of globe
        parent: Node object of parent
        f: path cost
        h: heuristic cost
        cost: total cost (f+h)
        step_from_parent: step or action taken from parent to reach current state
    
    #Funtions
        add_child: use to add child node of the current node
    
    """
    def __init__(self, state, parent, f, h, cost, step_from_parent):
        self.state = state
        self.parent = parent
        self.f = f
        self.h = h
        self.cost = cost
        self.step_from_parent = step_from_parent
        self.child = []
    """
    def __repr__(self):
        return str(self.state)
    """
    def __lt__(self, node2):
        return self.cost < node2.cost

    def add_child(self, child_state, f, h, cost, step_from_parent):
        """
        Function to add child of the node
        """
        self.child.append(
            Node(child_state, self.state, f, h, cost, step_from_parent))


#All 3 axis having tile positions belonging to it
longitude0_180 = {(0, 0), (30, 0), (60, 0), (90, 0), (120, 0), (150, 0),
                  (180, 180), (150, 180), (120, 180), (90, 180), (60, 180),
                  (30, 180)}
longitude90_270 = {(0, 0), (30, 90), (60, 90), (90, 90), (120, 90), (150, 90),
                   (180, 180), (150, 270), (120, 270), (90, 270), (60, 270),
                   (30, 270)}
equator = {(90, 0), (90, 30), (90, 60), (90, 90), (90, 120), (90, 150),
           (90, 180), (90, 210), (90, 240), (90, 270), (90, 300), (90, 330)}


def get_input_goal_state_from_file(file_path):
    """
    This function is used parse input file from the file path given to get input state.
    
    #Arguments
        file_path: path of the input file
        
    #Returns
        input_state: input state in form of 30X2 matrix
        goal_state: goal state in form of 30X2 matrix
    """
    with open(file_path) as f:
        input_lines = f.readlines()
    input_state = []
    goal_state = []
    for line in input_lines[1:len(input_lines) - 1]:
        line = line[5:len(line) - 2].split(', ')
        line[1] = line[1][1:len(line[1]) - 1].split(',')
        line[2] = line[2][6:len(line[2]) - 1].split(',')
        for (i, val) in enumerate(line[1]):
            line[1][i] = int(val)
        for (i, val) in enumerate(line[2]):
            line[2][i] = int(val)
        input_state.append([line[1][0], line[1][1]])
        goal_state.append([line[2][0], line[2][1]])
    return input_state, goal_state


def get_axis_dicts():
    """
    It is utility function return all dicts consisting next position of respective tiles when axis is rolled
    
    #Arguments
        No arguments
        
    #Returns
        long0_180_roll_dict: longitude0/180 axis when rolled clockwise (incremented)
        long90_270_roll_dict: longitude90/270 axis when rolled clockwise (incremented)
        equa_roll_dict: equator axis when rolled clockwise (incremented)
        long0_180_roll_dict_rev: longitude0/180 axis when rolled anti-clockwise (decremented)
        long90_270_roll_dict_rev: longitude90/270 axis when rolled anti-clockwise (decremented)
        equa_roll_dict_rev: equator axis when rolled anti-clockwise (decremented)
        
    Note: All return variables are dictionary which contains next tile position when correspoding axis is rolled
    """
    long0_180_roll_dict = {
        (0, 0): (30, 0),
        (30, 0): (60, 0),
        (60, 0): (90, 0),
        (90, 0): (120, 0),
        (120, 0): (150, 0),
        (150, 0): (180, 180),
        (180, 180): (150, 180),
        (150, 180): (120, 180),
        (120, 180): (90, 180),
        (90, 180): (60, 180),
        (60, 180): (30, 180),
        (30, 180): (0, 0)
    }

    long90_270_roll_dict = {
        (0, 0): (30, 90),
        (30, 90): (60, 90),
        (60, 90): (90, 90),
        (90, 90): (120, 90),
        (120, 90): (150, 90),
        (150, 90): (180, 180),
        (180, 180): (150, 270),
        (150, 270): (120, 270),
        (120, 270): (90, 270),
        (90, 270): (60, 270),
        (60, 270): (30, 270),
        (30, 270): (0, 0)
    }

    equa_roll_dict = {
        (90, 0): (90, 30),
        (90, 30): (90, 60),
        (90, 60): (90, 90),
        (90, 90): (90, 120),
        (90, 120): (90, 150),
        (90, 150): (90, 180),
        (90, 180): (90, 210),
        (90, 210): (90, 240),
        (90, 240): (90, 270),
        (90, 270): (90, 300),
        (90, 300): (90, 330),
        (90, 330): (90, 0)
    }
    #reverse dict is required when ring is decremented
    long0_180_roll_dict_rev = {
        value: key
        for key, value in long0_180_roll_dict.items()
    }
    long90_270_roll_dict_rev = {
        value: key
        for key, value in long90_270_roll_dict.items()
    }
    equa_roll_dict_rev = {value: key for key, value in equa_roll_dict.items()}
    return long0_180_roll_dict, long90_270_roll_dict, equa_roll_dict, long0_180_roll_dict_rev, long90_270_roll_dict_rev, equa_roll_dict_rev


long0_180_roll_dict, long90_270_roll_dict, equa_roll_dict, long0_180_roll_dict_rev, long90_270_roll_dict_rev, equa_roll_dict_rev = get_axis_dicts(
)

#List of the axis required to calculate how much number of moves apart 2 tiles are
long0_180 = list(long0_180_roll_dict.keys())
long90_270 = list(long90_270_roll_dict.keys())
equa = list(equa_roll_dict.keys())


def get_state_string(state):
    """
    Function converts the 30X2 matrix into string representation for low memory storage
    It is required, because due to this we use less memory. No need to store whole object
    #Arguments
        state: 30X2 matrix of current state
    
    #Returns
        state_string: string representation of the state given in argument
    """
    if state is None:
        return 'R'
    state_string = ''
    for coord in state:
        state_string = state_string + '_(' + str(coord[0]) + ', ' + str(
            coord[1]) + ')'
    return state_string[1:]


def roll_axis(current_state, axis_dict):
    """
    This function generates new state by rolling any axis in any directions based on the arguments passed
    The action depends upon which axis dict is passed
    
    #Arguments
        current_state: current state 2D matrix from which new state is to be generated
        axis_dict: it is one of the 6 dicts which stores the next position of each tile for single axis.
    
    #Returns
        new_state: new state after changing position of all tiles present in the axis which is rolled
    """
    #It changes the tile position of the tile present in the dict passes
    new_state = [
        list(axis_dict[tuple(tile_pos)])
        if tuple(tile_pos) in axis_dict else list(tile_pos)
        for tile_pos in current_state
    ]
    return new_state


def get_next_states(state):
    """
    This function generated all six possible new states using roll_axis function
    All 6 dicts are passed one by one to roll all 3 axis of the globe in clock and anti-clock direction
    
    #Arguments
        state: 2D matrix of the current state
    
    #Returns
        next_states: all 6 next states expanded from the state passed in the argument
        steps: Respective steps taken to get into next state from the current state
    """
    next_states = [
        roll_axis(state, long0_180_roll_dict),  #Longitute0/180 increase
        roll_axis(state, long0_180_roll_dict_rev),  #Longitute0/180 decrease
        roll_axis(state, long90_270_roll_dict),  #Longitute90/270 increase
        roll_axis(state, long90_270_roll_dict_rev),  #Longitute90/270 decrease
        roll_axis(state, equa_roll_dict),  #Equator increase
        roll_axis(state, equa_roll_dict_rev)  #Equator decrease
    ]
    #Steps takes to reach the next state. Order is same as the order of next states list above
    steps = [
        'long0_180_inc', 'long0_180_dec', 'long90_270_inc', 'long90_270_dec',
        'equa_inc', 'equa_dec'
    ]
    return next_states, steps


def get_path_steps(globe_dict):
    """
    It is used to get path and steps from the dictionary which stores following for the each state:
    1) parent state string
    2) path cost of the state
    3) step taken from parent to reach this state
    
    #Arguments
        globe_dict: dictionary which stores 3 things mentioned above for each state
    
    #Returns
        path: path in form of string represenation of state from start to goal satte
        steps: all steps from the start state to goal state
    """
    #It traverse the globe dict from the goal state to start state and takes out path and steps for each state.
    #Refer what is store in globe dict to better understand the structure of globe dict
    string = goal_state_string
    path = [string]
    steps = []
    while string != 'R':
        path = [globe_dict[string][0]] + path
        steps = [globe_dict[string][2]] + steps
        string = globe_dict[string][0]
    return path, steps + ['goal']


def bfs():
    """
    Bread-First search algorithm for solving the globe puzzle
    
    #Arguments
        No arguments
    
    #Returns
        num_state_expanded: Total number of states expanded to reach goal
        max_length_queue: Maximum length of the queue anytime during execution of algorithm
        globe_dict: dictionary to keep track of parent, path cost and step taken from parent 
        compute_time: Total time taken to reach goal state by the algorithm
    """
    start_time = time.time()
    globe_dict = dict()
    queue = [Node(input_state, None, None, None, 0, 'start')]
    plevel = -1  #This is just for debugging
    max_length_queue = 0
    num_state_expanded = 0
    while len(queue) != 0:
        max_length_queue = len(
            queue) if len(queue) > max_length_queue else max_length_queue
        current_state_node = queue.pop()
        num_state_expanded += 1  #Increase the state expanded by 1
        current_state_string = get_state_string(current_state_node.state)
        previous_state_string = get_state_string(current_state_node.parent)
        current_state_node.parent = None  #Dereference parent state variable as it is not required, to free up memory
        #--Debugging block start
        if plevel != current_state_node.cost:
            plevel = current_state_node.cost
            print("Current level: ", current_state_node.cost)
        #--Debugging block end
        #Check for the goal
        if current_state_string == goal_state_string:
            globe_dict[current_state_string] = [
                previous_state_string, current_state_node.cost,
                current_state_node.step_from_parent
            ]
            print("Hurray!! I reached my goal")
            break
        #Check if the current state is not already visited
        if current_state_string not in globe_dict:
            globe_dict[current_state_string] = [
                previous_state_string, current_state_node.cost,
                current_state_node.step_from_parent
            ]  #Insert state in globe dict to remember that this is visited
            new_states, steps = get_next_states(
                current_state_node.state)  #Get child states
            for state, step in zip(new_states, steps):
                current_state_node.add_child(state, None, None,
                                             current_state_node.cost + 1,
                                             step)
            queue = current_state_node.child + queue  #Add child states to the queue
    end_time = time.time()
    return num_state_expanded, max_length_queue, globe_dict, end_time - start_time


def heuristics(state, goal_state, long0_180, long90_270, equa):
    """
    This is the heuristics funtion which returns heuristic cost of each state to reach goal
    
    #Arguments
        state: state of which heuristic cost is to be calculated
        goal_state: goal state of the globe
        long0_180: list of tuple of longitude0/180 axis having tuples in order of rotation
        long90_270: list of tuple of longitude90/270 axis having tuples in order of rotation
        equa: set list of tuple of equator axis having tuples in order of rotation
    
    #Returns
        cost: heuristic cost of the state
    """
    """
    Explanation for cost calculation for each condition expect when both current tile and goal tile are in same ring
    
    temp_c11 = minimum move required to reach from current tile position to common tile1 either by increasing or decreasing ring
    temp_c21 = minimum move required to reach from current tile position to common tile2 either by increasing or decreasing ring
    temp_c12 = minimum move required to reach from common tile1 position to goal position either by increasing or decreasing ring
    temp_c22 = minimum move required to reach from commpn tile2 position to goal position either by increasing or decreasing ring
    
    Total there are 2 paths, minimum of 2 path is taken into consideration
    """
    cost = 0
    smoothing_constant = 8
    for (i, tile_pos) in enumerate(goal_state):
        tile_pos = tuple(tile_pos)
        state_tuple = tuple(state[i])
        if tile_pos in longitude0_180:
            if state_tuple in longitude0_180:
                cost += min(abs(long0_180.index(state_tuple)-long0_180.index(tile_pos)), len(long0_180)-abs(long0_180.index(state_tuple)-long0_180.index(tile_pos)))
            elif state_tuple in longitude90_270:
                temp_c11 = min(abs(long90_270.index((0,0))-long90_270.index(state_tuple)), len(long90_270)-abs(long90_270.index((0,0))-long90_270.index(state_tuple)))
                temp_c21 = min(abs(long90_270.index((180,180))-long90_270.index(state_tuple)), len(long90_270)-abs(long90_270.index((180,180))-long90_270.index(state_tuple)))
                temp_c12 = min(abs(long0_180.index((0,0))-long0_180.index(tile_pos)), len(long0_180)-abs(long0_180.index((0,0))-long0_180.index(tile_pos)))
                temp_c22 = min(abs(long0_180.index((180,180))-long0_180.index(tile_pos)), len(long0_180)-abs(long0_180.index((180,180))-long0_180.index(tile_pos)))
                cost += min(temp_c11+temp_c12, temp_c21+temp_c22)
            else:
                temp_c11 = min(abs(equa.index((90,0))-equa.index(state_tuple)), len(equa)-abs(equa.index((90,0))-equa.index(state_tuple)))
                temp_c21 = min(abs(equa.index((90,180))-equa.index(state_tuple)), len(equa)-abs(equa.index((90,180))-equa.index(state_tuple)))
                temp_c12 = min(abs(long0_180.index((90,0))-long0_180.index(tile_pos)), len(long0_180)-abs(long0_180.index((90,0))-long0_180.index(tile_pos)))
                temp_c22 = min(abs(long0_180.index((90,180))-long0_180.index(tile_pos)), len(long0_180)-abs(long0_180.index((90,180))-long0_180.index(tile_pos)))
                cost += min(temp_c11+temp_c12, temp_c21+temp_c22)
        elif tile_pos in longitude90_270:
            if state_tuple in longitude90_270:
                cost += min(abs(long90_270.index(state_tuple)-long90_270.index(tile_pos)), len(long90_270)-abs(long90_270.index(state_tuple)-long90_270.index(tile_pos)))
            elif state_tuple in longitude0_180:
                temp_c11 = min(abs(long0_180.index((0,0))-long0_180.index(state_tuple)), len(long0_180)-abs(long0_180.index((0,0))-long0_180.index(state_tuple)))
                temp_c21 = min(abs(long0_180.index((180,180))-long0_180.index(state_tuple)), len(long0_180)-abs(long0_180.index((180,180))-long0_180.index(state_tuple)))
                temp_c12 = min(abs(long90_270.index((0,0))-long90_270.index(tile_pos)), len(long90_270)-abs(long90_270.index((0,0))-long90_270.index(tile_pos)))
                temp_c22 = min(abs(long90_270.index((180,180))-long90_270.index(tile_pos)), len(long90_270)-abs(long90_270.index((180,180))-long90_270.index(tile_pos)))
                cost += min(temp_c11+temp_c12, temp_c21+temp_c22)
            else:
                temp_c11 = min(abs(equa.index((90,90))-equa.index(state_tuple)), len(equa)-abs(equa.index((90,90))-equa.index(state_tuple)))
                temp_c21 = min(abs(equa.index((90,270))-equa.index(state_tuple)), len(equa)-abs(equa.index((90,270))-equa.index(state_tuple)))
                temp_c12 = min(abs(long90_270.index((90,90))-long90_270.index(tile_pos)), len(long90_270)-abs(long90_270.index((90,90))-long90_270.index(tile_pos)))
                temp_c22 = min(abs(long90_270.index((90,270))-long90_270.index(tile_pos)), len(long90_270)-abs(long90_270.index((90,270))-long90_270.index(tile_pos)))
                cost += min(temp_c11+temp_c12, temp_c21+temp_c22)
        else:
            if state_tuple in equator:
                cost += min(abs(equa.index(state_tuple)-equa.index(tile_pos)), len(equa)-abs(equa.index(state_tuple)-equa.index(tile_pos)))
            elif state_tuple in longitude90_270:
                temp_c11 = min(abs(long90_270.index((90,90))-long90_270.index(state_tuple)), len(long90_270)-abs(long90_270.index((90,90))-long90_270.index(state_tuple)))
                temp_c21 = min(abs(long90_270.index((90,270))-long90_270.index(state_tuple)), len(long90_270)-abs(long90_270.index((90,270))-long90_270.index(state_tuple)))
                temp_c12 = min(abs(equa.index((90,90))-equa.index(tile_pos)), len(equa)-abs(equa.index((90,90))-equa.index(tile_pos)))
                temp_c22 = min(abs(equa.index((90,270))-equa.index(tile_pos)), len(equa)-abs(equa.index((90,270))-equa.index(tile_pos)))
                cost += min(temp_c11+temp_c12, temp_c21+temp_c22)
            else:
                temp_c11 = min(abs(long0_180.index((90,0))-long0_180.index(state_tuple)), len(long0_180)-abs(long0_180.index((90,0))-long0_180.index(state_tuple)))
                temp_c21 = min(abs(long0_180.index((90,180))-long0_180.index(state_tuple)), len(long0_180)-abs(long0_180.index((90,180))-long0_180.index(state_tuple)))
                temp_c12 = min(abs(equa.index((90,0))-equa.index(tile_pos)), len(equa)-abs(equa.index((90,0))-equa.index(tile_pos)))
                temp_c22 = min(abs(equa.index((90,180))-equa.index(tile_pos)), len(equa)-abs(equa.index((90,180))-equa.index(tile_pos)))
                cost += min(temp_c11+temp_c12, temp_c21+temp_c22)
    return cost/smoothing_constant


def astar():
    """
    A* algorithm for solving globe puzzle 
    
    #Arguments
        No arguments
    
    #Returns
        num_state_expanded: Total number of states expanded to reach goal
        max_length_queue: Maximum length of the queue anytime during execution of algorithm
        globe_dict: dictionary to keep track of parent, path cost and step taken from parent 
        compute_time: Total time taken to reach goal state by the algorithm
    """
    start_time = time.time()
    globe_dict = dict()
    plevel = -1
    max_length_queue = 0
    num_state_expanded = 0
    h = heuristics(input_state, goal_state, long0_180, long90_270, equa)
    heap_queue = [Node(input_state, None, 0, h, h, 'start')]
    while len(heap_queue) != 0:
        max_length_queue = len(heap_queue) if len(
            heap_queue) > max_length_queue else max_length_queue
        current_state_node = heappop(heap_queue)  #Always choose the best node from the heap
        num_state_expanded += 1
        current_state_string = get_state_string(current_state_node.state)
        previous_state_string = get_state_string(current_state_node.parent)
        current_state_node.parent = None  #Dereference parent state variable as it is not required, to free up memory
        #--Debugging block starts
        if plevel != current_state_node.f:
            plevel = current_state_node.f
            print("Current level: ", current_state_node.f)
        #--Debugging block ends
        #check for the goal
        if current_state_string == goal_state_string:
            globe_dict[current_state_string] = [
                previous_state_string, current_state_node.f,
                current_state_node.step_from_parent
            ]
            print("Hurray!! I reached my goal")
            break
        #check if current node is not already visited
        """
        Here algorithm does not check if the node cost is less than the node cost present in the dict because
        path cost is uniform, at every next level it increases to 1 and if new node is already present in 
        globe dict then heuristic cost will remain same. Therefore total cost of new will always be high than
        the node present in the dict
        """
        if current_state_string not in globe_dict:
            globe_dict[current_state_string] = [
                previous_state_string, current_state_node.f,
                current_state_node.step_from_parent
            ]
            new_states, steps = get_next_states(current_state_node.state)
            for state, step in zip(new_states, steps):
                f = current_state_node.f + 1  #Path cost
                h = heuristics(state, goal_state, long0_180, long90_270,
                               equa)  #Heuristic cost
                current_state_node.add_child(state, f, h, (f + h), step)
            for child_node in current_state_node.child:
                heappush(heap_queue, child_node)  #Push new node in heap
    end_time = time.time()
    return num_state_expanded, max_length_queue, globe_dict, end_time - start_time


def rbfs(current_state_node, cost_limit, plevel, num_state_expanded,
         max_length_queue, path, steps):
    current_state_string = get_state_string(current_state_node.state)
    #--Debugging block starts
    if plevel != current_state_node.f:
        print("Current Level: ", current_state_node.f)
        plevel = current_state_node.f
    #--Debugging block ends
    #check for the goal state
    if current_state_string == goal_state_string or time.time()-start_time > 1800:
        print("Hurray!! I reached my goal")
        #Algorithm back tracks to start state so take the path and steps
        path = [current_state_string] + path
        steps = [current_state_node.step_from_parent] + steps
        return goal_state_string, current_state_node.cost, path, steps, num_state_expanded, max_length_queue
    new_states, steps_from_parent = get_next_states(current_state_node.state)  #Get child states
    next_states = []
    for state, step in zip(new_states, steps_from_parent):
        f = current_state_node.f + 1  #Path cost
        h = heuristics(state, goal_state, long0_180, long90_270, equa)  #Heuristic cost
        current_state_node.add_child(state, f, h, max(f + h, current_state_node.cost), step)
        current_state_node.child[-1].parent = None  #Dereference parent state variable as it is not required, to free up memory
        heappush(next_states, current_state_node.child[-1])  #Push each child to heap
    max_queue_length_instance = 0
    while True:
        #Max queue length
        max_queue_length_instance = max(max_queue_length_instance, len(next_states))
        best_node = heappop(next_states)  #Take out the best node
        #If best node exceeds the cost limit then do not expand this node further
        if best_node.cost > cost_limit:
            return None, best_node.cost, path, steps, num_state_expanded, max_length_queue
        second_best_node = next_states[0]  #Take the second best node
        #Now update the cost limit to the cost of second best node if its cost is less than current cost limit
        new_cost_limit = min(cost_limit, second_best_node.cost)
        num_state_expanded += 1
        goal_string, best_node.cost, path, steps, num_state_expanded, max_length_queue = rbfs(
            best_node, new_cost_limit, plevel, num_state_expanded,
            max_length_queue, path, steps)
        heappush(next_states, best_node) #Push the best node again with the new cost propogated from the child node
        max_length_queue += max_queue_length_instance
        if goal_string is not None:
            path = [current_state_string] + path
            steps = [current_state_node.step_from_parent] + steps
            return goal_string, best_node.cost, path, steps, num_state_expanded, max_length_queue


def recursive_best_first_search():
    """
    Recursive best first search algorithm to solve the globe puzzle
    
    #Arguments
        No arguments
    
    #Returns
        total_cost: total cost to reach the goal
        path: path to reach goal state from start state
        steps: Steps taken from start state to goal state
    """
    start_time = time.time()
    path = []
    steps = []
    max_length_queue = 0
    num_state_expanded = 0
    h = heuristics(input_state, goal_state, long0_180, long90_270, equa)
    current_state_node = Node(input_state, None, 0, h, h, 'start')
    goal_string, total_cost, path, steps, num_state_expanded, max_length_queue = rbfs(
        current_state_node, 10000000, 0, num_state_expanded, max_length_queue,
        path, steps)
    end_time = time.time()
    return total_cost, path + [goal_string], steps + [
        'goal'], num_state_expanded, max_length_queue, end_time - start_time


if __name__ == "__main__":
    input_state, goal_state = get_input_goal_state_from_file(file_path)
    goal_state_string = get_state_string(goal_state)
    start_time = time.time()
    if algo == 'BFS':
        num_state_expanded, max_length_queue, globe_dict, compute_time = bfs()
        path, steps = get_path_steps(globe_dict)
        path_length = len(path) - 2
    if algo == 'AStar':
        num_state_expanded, max_length_queue, globe_dict, compute_time = astar()
        path, steps = get_path_steps(globe_dict)
        path_length = len(path) - 2
    if algo == 'RBFS':
        cost, path, steps, num_state_expanded, max_length_queue, compute_time = recursive_best_first_search()
        path_length = len(path) - 2
    print("Reached goal in " + str(compute_time) + "seconds")
    print("Number of states expanded:", num_state_expanded)
    print("Maximum length of queue:", max_length_queue)
    print("Length of the path:", path_length)
    print("Steps to goal:")
    steps_string = ""
    for (i, step) in enumerate(steps):
        if i == 0:
            steps_string = step
        else:
            steps_string = steps_string + " -> " + step
    print(steps_string)