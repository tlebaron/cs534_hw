import copy

def getNodeIndex(graph, s_node):
    index = 0
    for node in graph:
	if node[0] == s_node:
	    return index
	index += 1

    graph.append([s_node])
    return index

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
	cost = int(cost)
	addEdge(graph, node1, node2, cost)

    for line in goal_dist_list:
	node = line.split()[0]
	distance = int(line.split()[1])
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



f = open("input.txt", "r")
graph = createGraph(f)



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

