from copy import deepcopy
import sys

class Node:

    def __init__(self, n, h):
	self.name = n
	self.heuristic = h

    @staticmethod
    def getNodeName(self):
	return self.name

    def getNodeHeuristic(self):
	return self.heuristic

    def isNode(self, n):
	return (self.name == n.name)

class Connection:

    def __init__(self, n1, n2, c):
	self.node1 = n1
	self.node2 = n2
	self.cost = c

class Path:

    def __init__(self, node, g):
	self.graph = g
	self.nodes = [node]

    def addNode(self, node, pos = 0):
	self.nodes.insert(pos, node)

    def inPath(self, n):
	for node in self.nodes:
	    if node.name == n.name:
		return True
	return False

    def stringPath(self, graph, method_number):
	if method_number in [1, 2, 3, 4]:
	    string = ""
	elif method_number in [6, 8, 9]:
	    string = "{0}".format(self.nodes[0].heuristic)
	elif method_number in [5]:
	    string = "{0}".format(self.getTotalCost(self))
	elif method_number in [7]:
	    string = "{0}".format(self.getSumCostHeuristic(self))
	string += "<"
	for node in self.nodes:
	    string += str(node.name) + ","
	string = string[:-1] + ">"
	return string

    @staticmethod
    def getLength(self):
	return len(self.nodes)

    @staticmethod
    def getTotalCost(self):
	cost = 0
	for index in range(0, len(self.nodes)-1):
	    add_cost = self.graph.getCost(self.nodes[index], self.nodes[index+1])
	    assert add_cost >= 0
	    cost += add_cost
	return cost

    @staticmethod
    def getFinalHeuristic(self):
	return self.nodes[0].heuristic

    @staticmethod
    def getSumCostHeuristic(self):
	return self.getFinalHeuristic(self) + self.getTotalCost(self)

    @staticmethod
    def getFirstNodeName(self):
	return self.nodes[0].name

class Queue:

    def __init__(self, node, g):
	self.graph = g
	self.path_list = [Path(node, g)]

    def getPathByLength(self, l):
	return_list = []
	for path in self.path_list:
	    if len(path.nodes) == l:
		return_list.append(path)
	return return_list

    def addPath(self, p, pos = -1):
	if pos == -1:
	    pos = len(self.path_list)
	self.path_list.insert(pos, p)

    def getNodeToExpand(self):
	firstPath = self.path_list[0]
	del self.path_list[0]
	return [firstPath.nodes[0], firstPath]

    def printQueue(self, graph, search_method_number):
	string = "\t{0}\t\t[".format(self.path_list[0].nodes[0].name)
	for path in self.path_list:
	    string += path.stringPath(graph, search_method_number) + " "
	string = string[:-1] + "]"
	print string
	
    def remove(self, p):
	for p_index, path in enumerate(self.path_list):
	    if path == p:
		del self.path_list[p_index]

    def sortQueue(self, param = 0):
	# param = 1 for cost so far
	# param = 2 for heuristic
	# param = 3 for cost so far + heuristic
	self.path_list = sorted(self.path_list, key = Path.getLength)
	self.path_list = sorted(self.path_list, key = Path.getFirstNodeName)
	if param == 1:
	    self.path_list = sorted(self.path_list, key = Path.getTotalCost)
	if param == 2:
	    self.path_list = sorted(self.path_list, key = Path.getFinalHeuristic)
	if param == 3:
	    self.path_list = sorted(self.path_list, key = Path.getSumCostHeuristic)

class Problem:

    def __init__(self, gr, s, g, p = []):
	self.graph = gr
	self.source = s
	self.goal = g
	self.param = p

class Graph:

    nodes = []
    connections = []

    def addNode(self, node):
	self.nodes.append(node)

    def addConnection(self, node1, node2, cost):
	self.connections.append(Connection(node1, node2, cost))
	self.connections.append(Connection(node2, node1, cost))

    def getCost(self, n1, n2):
	for connection in self.connections:
	    if connection.node1.isNode(n1) and connection.node2.isNode(n2):
		return connection.cost
	return 0

    def getNodeByName(self, n):
	for node in self.nodes:
	    if node.name == n:
		return node

    def isIn(self, n):
	for node in self.nodes:
	    if node == n:
		return True
	return False

    def printGraph(self):
	for node in self.nodes:
	    print node.name
	

def createGraph(f):

    lines = []
    for line in f.readlines():
	lines.append(line[:-1])

    path_list = lines[:lines.index('#####')]
    goal_dist_list = lines[lines.index('#####')+1:]

    graph = Graph()

    for line in goal_dist_list:
	node_name = line.split()[0]
	distance = float(line.split()[1])
	graph.addNode(Node(node_name, distance))

    graph.addNode(Node('G', 0))

    for line in path_list:
	[node1, node2, cost] = line.split()
	cost = float(cost)
	n1 = graph.getNodeByName(node1)
	n2 = graph.getNodeByName(node2)
	graph.addConnection(n1, n2, cost)

    return graph

def expand(graph, node, path):
    opened_nodes = []

    for connection in graph.connections:
	if connection.node1.isNode(node) and not path.inPath(connection.node2):
	    opened_nodes.append(connection.node2)

    return sorted(opened_nodes, key = Node.getNodeName)

def depthFirstHandler(queue, opened_nodes, current_path, parameters):
    opened_nodes = sorted(opened_nodes, key = Node.getNodeName)[::-1]

    for node in opened_nodes:
	path = deepcopy(current_path)
	path.addNode(node, 0)
	queue.addPath(path, 0)
	
    return queue

def breadthFirstHandler(queue, opened_nodes, current_path, parameters):
    opened_nodes = sorted(opened_nodes, key = Node.getNodeName)

    for node in opened_nodes:
	path = deepcopy(current_path)
	path.addNode(node, 0)
	queue.addPath(path)
	
    return queue

def depthLimitedHandler(queue, opened_nodes, current_path, parameters):
    #parameters[0] is the path max length

    opened_nodes = sorted(opened_nodes, key = Node.getNodeName)[::-1]

    for node in opened_nodes:
	path = deepcopy(current_path)
	path.addNode(node, 0)
	if len(path.nodes) > parameters[0]+1:
	    continue
	queue.addPath(path, 0)
	
    return queue

def iterativeHandler(queue, opened_nodes, current_path, parameters):
    '''
    #parameters[0] is the current path max length

    queue = depthLimitedHandler(queue, opened_nodes, current_path, parameters)
    if len(queue.path_list) == 0:
	parameters[0] += 1
	queue.printDepth(parameters[0])
	queue = depthLimitedHandler(queue, opened_nodes, current_path, parameters)

    return queue
    '''

def uniformHandler(queue, opened_nodes, current_path, parameters):
    opened_nodes = sorted(opened_nodes, key = Node.getNodeName)[::-1]

    for node in opened_nodes:
	path = deepcopy(current_path)
	path.addNode(node, 0)
	queue.addPath(path)

    queue.sortQueue(1)
	
    return queue

def greedyHandler(queue, opened_nodes, current_path, parameters):
    opened_nodes = sorted(opened_nodes, key = Node.getNodeName)[::-1]

    for node in opened_nodes:
	path = deepcopy(current_path)
	path.addNode(node, 0)
	queue.addPath(path, 0)

    queue.sortQueue(2)
	
    return queue

def aStarHandler(queue, opened_nodes, current_path, parameters):
    opened_nodes = sorted(opened_nodes, key = Node.getNodeName)[::-1]

    for node in opened_nodes:
	path = deepcopy(current_path)
	path.addNode(node, 0)
	queue.addPath(path, 0)

    queue.sortQueue(3)
	
    return queue

def hillClimbingHandler(queue, opened_nodes, current_path, parameters):
    if len(opened_nodes) == 0:
	return queue

    opened_nodes = sorted(opened_nodes, key = Node.getNodeName)[::-1]

    best_node = opened_nodes[0]

    for node in opened_nodes:
	if node.heuristic < best_node.heuristic:
	    best_node = node
    path = deepcopy(current_path)
    path.addNode(best_node, 0)
    queue.addPath(path, 0)
	
    return queue

def beamHandler(queue, opened_nodes, current_path, parameters):
    #parameters[0] is the number of best node to keep
    #the next n are the best path kept until now, in the right order.
    opened_nodes = sorted(opened_nodes, key = Node.getNodeName)

    for node in opened_nodes:
	same_length_path = queue.getPathByLength(len(current_path.nodes) + 1)
	if len(same_length_path) < parameters[0]:
	    path = deepcopy(current_path)
	    path.addNode(node, 0)
	    queue.addPath(path)
	    continue
	w_path = max(same_length_path, key = Path.getFinalHeuristic)
	if w_path.getFinalHeuristic(w_path) > node.heuristic:
	    del queue.path_list[queue.path_list.index(w_path)]
	    path = deepcopy(current_path)
	    path.addNode(node, 0)
	    queue.addPath(path)

    return queue

reorderQueue = {
1: depthFirstHandler,
2: breadthFirstHandler,
3: depthLimitedHandler,
4: iterativeHandler,
5: uniformHandler,
6: greedyHandler,
7: aStarHandler,
8: hillClimbingHandler,
9: beamHandler
}


def General_Search(problem, search_method):

    print "\tExpanded\tQueue"

    queue = Queue(problem.source, problem.graph)

    while True:
	if len(queue.path_list) == 0:
	    return -1
	queue.printQueue(problem.graph, search_method)
	[current_node, current_path] = queue.getNodeToExpand()
	if current_node.isNode(problem.goal):
	    return current_node

	opened_nodes = expand(problem.graph, current_node, current_path)
	queue = reorderQueue[search_method](queue, opened_nodes, current_path, problem.param)


def depthFirstSearch(problem):
    return General_Search(problem, 1)

def breadthFirstSearch(problem):
    return General_Search(problem, 2)

def depthLimitedSearch(problem, p = 2):
    problem.param = [p]
    return General_Search(problem, 3)

def iterativeSearch(problem):
    # /!\ assume that one solution exists !!
    print "L = 0"
    counter = 0
    while True:
	problem.param = [counter]
	res = depthLimitedSearch(problem, counter)
	if res == problem.goal:
	    return res
	else:
	    counter += 1
	    print "L = {0}".format(counter)

def uniformSearch(problem):
    return General_Search(problem, 5)

def greedySearch(problem):
    return General_Search(problem, 6)

def aStarSearch(problem):
    return General_Search(problem, 7)

def hillClimbingSearch(problem):
    return General_Search(problem, 8)

def beamSearch(problem, p = 2):
    problem.param = [p]
    return General_Search(problem, 9)


def main():
    if len(sys.argv) != 2:
	print "Usage: python searchScript.py {input file} [-o {output file}]"
	return

    try:
	f = open(sys.argv[1], "r")
    except Exception:
	pass

    graph = createGraph(f)
    goal = graph.getNodeByName('G')
    source = graph.getNodeByName('S')

    print "\nDepth first search"
    if depthFirstSearch(Problem(graph, source, goal)) == goal:
	print "\tgoal reached!"

    print "\nBreadth first search"
    if breadthFirstSearch(Problem(graph, source, goal)) == goal:
	print "\tgoal reached!"

    print "\nDepth limited search"
    if depthLimitedSearch(Problem(graph, source, goal,), 2) == goal:
	print "\tgoal reached!"

    print "\nIterative search"
    if iterativeSearch(Problem(graph, source, goal)) == goal:
	print "\tgoal reached!"

    print "\nUniform search"
    if uniformSearch(Problem(graph, source, goal)) == goal:
	print "\tgoal reached!"

    print "\nGreedy search"
    if greedySearch(Problem(graph, source, goal)) == goal:
	print "\tgoal reached!"

    print "\nA* search"
    if aStarSearch(Problem(graph, source, goal)) == goal:
	print "\tgoal reached!"

    print "\nHill climbing search"
    if hillClimbingSearch(Problem(graph, source, goal)) == goal:
	print "\tgoal reached!"

    print "\nBeam search"
    if beamSearch(Problem(graph, source, goal), 2) == goal:
	print "\tgoal reached!"


if __name__ == '__main__':
    main()
