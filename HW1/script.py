import copy

def getNodeIndex(graph, s_node):
    index = 0
    for node in graph:
	if node[0] == s_node:
	    return index
	index += 1

    graph.append([s_node])
    return index

def getNodeDistance(graph, s_node, goal):
    if s_node == goal:
	return 0
    return graph[getNodeIndex(graph, s_node)][1]

def addEdge(graph, node1, node2, cost):
    graph[getNodeIndex(graph, node1)].insert(1,[node2, cost])
    graph[getNodeIndex(graph, node2)].insert(1,[node1, cost])

def sortGetNodeIndex(node):
    return node[0]

def getConnectedNodes(graph, node):
    return graph[getNodeIndex(graph, node)][2:]

def createGraph(f):

    lines = []
    for line in f.readlines():
	lines.append(line[:-1])


    path_list = lines[:lines.index('#####')]
    goal_dist_list = lines[lines.index('#####')+1:]

    graph = []
    for line in path_list:
	[node1, node2, cost] = line.split()
	cost = float(cost)
	addEdge(graph, node1, node2, cost)

    for line in goal_dist_list:
	node = line.split()[0]
	distance = float(line.split()[1])
	graph[getNodeIndex(graph, node)].insert(1,distance)
    for index in range(0, len(graph)):
	graph[index][2:] = sorted(graph[index][2:], key=sortGetNodeIndex)

    return graph

def printQueue(queue):
    string = "["
    for path in queue:
	string += "<"
	for node in path:
	    string += node+','
	string = string[:-1]
	string +="> "
    return string[:-1]+"]"

def depthFirstSearch(graph, source, goal):
    queue = [[source]]
    while len(queue) > 0:
	print "\t{0}\t\t\t{1}".format(queue[0][0], printQueue(queue))
	if queue[0][0] == goal:
	    print "\tgoal reached!"
	    return queue[0]
	else:
	    path_to_explore = queue[0][:]
	    del queue[0]
	    children_list = getConnectedNodes(graph, path_to_explore[0])[::-1]
	    for child in children_list:
		if child[0] not in path_to_explore:
		    new_path = path_to_explore[:]
		    new_path.insert(0,child[0])
		    
		    queue.insert(0,new_path)
	    
    return -1

def depthLimitSearch(graph, source, goal, limit):
    queue = [[source]]
    while len(queue) > 0:
	moreToAdd = False
	print "\t{0}\t\t\t{1}".format(queue[0][0], printQueue(queue))
	if queue[0][0] == goal:
	    print "\tgoal reached!"
	    return 1
	else:
	    path_to_explore = queue[0][:]
	    del queue[0]
	    children_list = getConnectedNodes(graph, path_to_explore[0])[::-1]
	    for child in children_list:
		if child[0] not in path_to_explore:
		    new_path = path_to_explore[:]
		    new_path.insert(0,child[0])
		    
		    if len(new_path) <= limit+1:
			queue.insert(0,new_path)
		    else:
			moreToAdd = True

    if moreToAdd:
	return 0
    return -1

def iterativeDeepeningSearch(graph, source, goal):
    iteration = 1
    while True:
	print "L = {0}".format(iteration-1)
	res = depthLimitSearch(graph, source, goal, iteration)
	iteration += 1
	if res != 0:
	    return

def breadthFirstSearch(graph, source, goal):
    queue = [[source]]
    while len(queue) > 0:
	print "\t{0}\t\t\t{1}".format(queue[0][0], printQueue(queue))
	if queue[0][0] == goal:
	    print "\tgoal reached!"
	    return queue[0]
	else:
	    path_to_explore = queue[0][:]
	    del queue[0]
	    children_list = getConnectedNodes(graph, path_to_explore[0])
	    for child in children_list:
		if child[0] not in path_to_explore:
		    new_path = path_to_explore[:]
		    new_path.insert(0,child[0])

		    queue.append(new_path)

    return -1


def printQueueCost(queue):
    string = "["
    for path in queue:
	string += str(path[0]) + "<"
	for node in path[1:]:
	    string += node+','
	string = string[:-1]
	string +="> "
    return string[:-1]+"]"


def uniformCostSearch(graph, source, goal):
    queue = [[0,source]]

    while len(queue) > 0:
	print "\t{0}\t\t\t{1}".format(queue[0][1], printQueueCost(queue))
	if queue[0][1] == goal:
	    print "\tgoal reached!"
	    return queue[0]
	else:
	    path_to_explore = queue[0][:]
	    del queue[0]
	    children_list = getConnectedNodes(graph, path_to_explore[1])
	    for child in children_list:
		if child[0] not in path_to_explore:
		    new_path = path_to_explore[:]
		    new_path.insert(1,child[0])
		    new_path[0] += child[1]

		    queue.append(new_path)
		    queue = sorted(queue, key=sortGetNodeIndex)
	
    return -1

def greedySearch(graph, source, goal):
    queue = [[getNodeDistance(graph, source, goal), source]]

    while len(queue) > 0:
	print "\t{0}\t\t\t{1}".format(queue[0][1], printQueueCost(queue))
	if queue[0][1] == goal:
	    print "\tgoal reached!"
	    return queue[0]
	else:
	    path_to_explore = queue[0][:]
	    del queue[0]
	    children_list = getConnectedNodes(graph, path_to_explore[1])
	    for child in children_list:
		if child[0] not in path_to_explore:
		    new_path = path_to_explore[:]
		    new_path.insert(1,child[0])
		    new_path[0] = getNodeDistance(graph, child[0], goal)

		    queue.append(new_path)
		    queue = sorted(queue, key=sortGetNodeIndex)
	
    return -1


def aStarSearch(graph, source, goal):
    queue = [[getNodeDistance(graph, source, goal), source]]

    while len(queue) > 0:
	print "\t{0}\t\t\t{1}".format(queue[0][1], printQueueCost(queue))
	if queue[0][1] == goal:
	    print "\tgoal reached!"
	    return queue[0]
	else:
	    path_to_explore = queue[0][:]
	    del queue[0]
	    children_list = getConnectedNodes(graph, path_to_explore[1])
	    for child in children_list:
		inOtherPath = False
		if child[0] not in path_to_explore:
		    for inc_path in queue:
			if child[0] in inc_path:
			    inOtherPath = True
		    if inOtherPath:
			continue
		    new_path = path_to_explore[:]
		    new_path.insert(1,child[0])
		    new_path[0] -= getNodeDistance(graph, path_to_explore[1], goal)
		    new_path[0] += child[1] + getNodeDistance(graph, child[0], goal)

		    queue.append(new_path)
		    queue = sorted(queue, key=sortGetNodeIndex)
	
    return -1


def hillClimbing(graph, source, goal):
    queue = [[getNodeDistance(graph, source, goal), source]]

    while len(queue) > 0:
	print "\t{0}\t\t\t{1}".format(queue[0][1], printQueueCost(queue))
	if queue[0][1] == goal:
	    print "\tgoal reached!"
	    return queue[0]
	else:
	    path_to_explore = queue[0][:]
	    del queue[0]
	    children_list = getConnectedNodes(graph, path_to_explore[1])
	    t_queue = []
	    for child in children_list:
		if child[0] not in path_to_explore:
		    new_path = path_to_explore[:]
		    new_path.insert(1,child[0])
		    new_path[0] = getNodeDistance(graph, child[0], goal)
		    t_queue.append(new_path)
	    t_queue = sorted(t_queue, key=sortGetNodeIndex)
	    queue.insert(0,t_queue[0])
	
    return -1


def getNBests(node_list, N):
    n_bests = []
    for node in node_list:
	n_bests.append(node)
	if len(n_bests) > N:
	    #remove worse
	    worst = n_bests[0]
	    for i_node in n_bests:
		if i_node[0] > worst[0]:
		    worst = i_node
	    del n_bests[n_bests.index(worst)]

    return n_bests


def beamSearch(graph, source, goal, w):
    queue = [[getNodeDistance(graph, source, goal), source]]
    size = len(queue[0]) -1
    while len(queue) > 0:
	print "\t{0}\t\t\t{1}".format(queue[0][1], printQueueCost(queue))
	if queue[0][1] == goal:
	    print "\tgoal reached!"
	    return queue[0]
	else:
	    path_to_explore = queue[0][:]
	    del queue[0]
	    children_list = getConnectedNodes(graph, path_to_explore[1])
	    list_new_path = []
	    for child in children_list:
		if child[0] not in path_to_explore:
		    new_path = path_to_explore[:]
		    new_path.insert(1,child[0])
		    new_path[0] = getNodeDistance(graph, child[0], goal)
		    queue.append(new_path)

	if size != len(queue[0])-1:
	    size = len(queue[0])-1
	    queue = getNBests(queue[:], w)

    return -1


f = open("input2.txt", "r")
graph = createGraph(f)


'''
print "\t## Depth first search ##"
print "\tExpanded\t\tQueue"
depthFirstSearch(graph, 'S', 'G')

print "\t## Breadth first search ##"
print "\tExpanded\t\tQueue"
breadthFirstSearch(graph, 'S', 'G')

print "\t## Depth limit search ##"
print "\tExpanded\t\tQueue"
depthLimitSearch(graph, 'S', 'G', 2)

print "\t## Iterative search ##"
print "\tExpanded\t\tQueue"
iterativeDeepeningSearch(graph, 'S', 'G')

print "\t## Uniform search ##"
print "\tExpanded\t\tQueue"
uniformCostSearch(graph, 'S', 'G')

print "\t## Greedy search ##"
print "\tExpanded\t\tQueue"
greedySearch(graph, 'S', 'G')

print "\t## A* search ##"
print "\tExpanded\t\tQueue"
aStarSearch(graph, 'S', 'G')

print "\t## Hill climbing ##"
print "\tExpanded\t\tQueue"
hillClimbing(graph, 'S', 'G')
'''

print "\t## Beam seach ##"
print "\tExpanded\t\tQueue"
beamSearch(graph, 'S', 'G',2)

