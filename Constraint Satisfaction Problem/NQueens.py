#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 20:49:52 2019

@author: shaivalshah
"""

"""
There are 2 algorithm FOC and MAC with backtracking
FOC:
    It checks the neighbors of the current node after assigning current node
    If the values in the domain of the neighbor node is not satisfying constraint
    with the currently assigned value then that values are removed from the 
    neighbor node
    The algorithm backtracks when there are no values remaining in the domain 
    of the current node to assign which satisfy the constraint.
    
MAC:
    After assigning value to the variable it forward checks the neighbor node
    and see which neighbor node domains can be reduce
    After that arcs of those neighbors are inserted in queue containing
    (neighbor->neighbor, neighbor)
    This queue is passed for AC3 algorithm to make the following arcs consistent
    
The results shows that backtracking steps of MAC is lesser 
"""

import copy
import sys
import time

class QueenGraph:
    def __init__(self):
        self.variables = ['Q' + str(i + 1) for i in range(N)]
        """
        domains only contains the row value of each queen, each variable represents each 
        queen which can be placed in fixed column
        Q1 can only be placed in 1st column, similarly Q2 in 2nd column and so on
        """
        self.domains = {'Q' + str(i + 1): [x for x in range(N)] for i in range(N)}
        self.removed_domains = {'Q' + str(i + 1): [] for i in range(N)} #used to backup the domains and its values which are removed
        self.neighbors = {xi: [] for xi in self.variables}
        for xi in self.variables:
            for xj in self.variables:
                if xi != xj:
                    self.neighbors[xi].append(xj)
        self.assignment = {} #stores the assignment of the variables
    
    def assign_val(self, var, val):
        self.assignment[var] = val
    
    def unassign_val(self, var):
        del self.assignment[var]
    
    def constraint_not_satisfied(self, var, val, v, dom_val):
        """
        This function checks if the two variables 'var' and 'v' are not conflicting with each other
        having value 'val' and 'dom_val' respectively.
        It checks the constraints which are mentioned in CFile
        """
        if val == dom_val:
            return True
        col1 = int(var[1:]) - 1
        col2 = int(v[1:]) - 1
        if val == dom_val - abs(col2 - col1) or val == dom_val + abs(col2 - col1):
            return True
        return False
    
    def forward_check(self, var, val):
        """
        removes the domain value of the neighbors of 'var' if it is conflicting with assignment of 'var'
        which is 'val'
        """
        for v in self.neighbors[var]:
            if v not in self.assignment:
                changed_domain = self.domains[v].copy()
                for dom_val in self.domains[v]:
                    if self.constraint_not_satisfied(var, val, v, dom_val):
                        changed_domain.remove(dom_val)
                        self.removed_domains[var].append((v, dom_val))
                self.domains[v] = changed_domain
                if len(self.domains[v]) == 0:
                    return False
        return True
    
    def AC3(self, queue, var):
        while queue:
            (xi,xj) = queue.pop(0)
            if self.revise(xi, xj, var):
                #If domain reduces to 0 return False to backtrack to previous values
                if len(self.domains[xi]) == 0:
                    return False
                #if there is change in domain add neighbors of the current node in the queue
                for v in set(self.neighbors[xi]) - {xj}:
                    queue.append((v, xi))
        return True
    
    def revise(self, xi, xj, var):
        revised = False
        changed_domain = self.domains[xi].copy()
        for x in self.domains[xi]:
            flag = False
            for y in self.domains[xj]:
                if not self.constraint_not_satisfied(xi, x, xj, y):
                    flag = True #It is used to check if any value satisfy the constraint
                    break
            if not flag:
                changed_domain.remove(x)
                #Store the removed value of the variable in the dict of variable 'var' 
                #due to which the domain value of xi is removed
                self.removed_domains[var].append((xi, x))
                revised = True
        self.domains[xi] = changed_domain
        return revised
    
    def check_solution(self):
        #checks if the all assignments are completed or not
        if len(self.assignment) == len(self.variables):
            return True
        return False
    

def get_unassigned_variables(queen_graph):
    #Get the variable which is not assigned before
    for v in queen_graph.variables:
        if v not in queen_graph.assignment:
            return v
    return None    


def solveNQueens(algo):
    #Main function to solve NQueens problem
    start_time = time.time()
    backtrack_search(algo, QueenGraph())
    end_time = time.time()
    return end_time - start_time

def backtrack_search(algo, queen_graph):
    global stop
    global backtracking_steps
    if queen_graph.check_solution():
        all_solutions.append(copy.deepcopy(queen_graph))
        #stop variable used to stop the algorithm to find solution if total number of solution reaches 2*N
        stop -= 1
        if stop == 0:
            return True 
        return False #algorithm returns false even if it finds solution to backtrack and find new solution
    var = get_unassigned_variables(queen_graph)
    for val in queen_graph.domains[var]:
        queen_graph.assign_val(var, val)
        if algo == 'FOC' and queen_graph.forward_check(var, val):
            if backtrack_search(algo, queen_graph):
                return True
        '''
        For MAC:
        First the forward check is passed to reduce the domain of the neighbors because of assignment
        After that neighbors of all neighbors of current variable whose domain reduced is passed in queue
        which is passed in AC3 algorithm to make further arc consistent
        '''
        if algo == 'MAC' and queen_graph.forward_check(var, val):
            queue = []
            for (v, dom_val) in queen_graph.removed_domains[var]:
                for xk in set(queen_graph.neighbors[v]) - {var}:
                    queue.append((xk, v))
            if queen_graph.AC3(queue, var):
                if backtrack_search(algo, queen_graph):
                    return True
        queen_graph.unassign_val(var)
        #if the assignment fails restore the removed values from the domains of the variables
        for (v, dom_val) in queen_graph.removed_domains[var]:
            queen_graph.domains[v].append(dom_val)
        queen_graph.removed_domains[var] = []
    backtracking_steps += 1
    return False


def store_results(time_taken):
    with open(RFile, 'w') as f:
        f.write("Algorithm: Backtracking using "+algo+"\n")
        f.write("Size: "+str(N)+"\n\n")
        f.write("Number of solutions found: " + str(len(all_solutions))+"\n")
        f.write("Real time taken: "+str(time_taken)+" seconds\n")
        f.write("Backtracking Steps: " + str(backtracking_steps)+"\n\n")
        f.write("Solutions:\n\n")
        for i, solution in enumerate(all_solutions):
            f.write("Solution " + str(i+1) +":\n\n")
            sol_mat = [[0 for x in range(N)] for y in range(N)]
            for q, pos in solution.assignment.items():
                row = int(q[1:]) - 1
                sol_mat[row][pos] = 1
            for row in sol_mat:
                f.write("\t" + str(row) + "\n")
            f.write("\n")


def store_constraints():
    with open(CFile, 'w') as f:
        f.write("Variables: " + str(["Q"+str(i+1) for i in range(N)]) + "\n\n")
        f.write("Domains:\n")
        for i in range(N):
            f.write("Q"+str(i+1)+": [")
            for j in range(N):
                if j == N-1:
                    f.write(str(j))
                else:
                    f.write(str(j)+", ")
            f.write("]\n")
        f.write("\nConstraint:\nQi != Qj\n")
        f.write("|Qj - Qi| != |j-i|\nwhere 1 <= i,j <= N\n\n")
        for i in range(1, N+1):
            for j in range(i+1, N+1):
                f.write("Q"+str(i) + "!= Q" + str(j) + "\n")
                f.write("|Q"+str(j) + "- Q"+str(i) + "| != " + str(j-i) + "\n")


if __name__ == "__main__":
    algo = sys.argv[1]
    N = int(sys.argv[2])
    CFile = sys.argv[3]
    RFile = sys.argv[4]

    stop = 2*N
    all_solutions = []
    backtracking_steps = 0
    time_taken = solveNQueens(algo)
    store_results(time_taken)
    store_constraints()
    print("Algo: ", algo)
    print("Size: ",N)
    print("Number of solutions found: " + str(len(all_solutions)))
    print("Real time taken: "+str(time_taken)+" seconds")
    print("Backtracking Steps: " + str(backtracking_steps))
    print("\nSolutions\n")
    for sol in all_solutions:
        print(sol.assignment)