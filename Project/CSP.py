import sys
import re

class Variable:

	def __init__(self, list_args):
		self.name = list_args[0]
		self.args = list_args[1:]

	def __repr__(self):
		return "Variable({0},{1})".format(self.name, self.args)
		

class Value:

	def __init__(self, n):
		self.name = n

	def __repr__(self):
		return "Value({0})".format(self.name)


class Constraint:

	# types of constraints:
	#	0: deadline, universal
	#	11: Unary inclusive --- the task can only be assigned this subset of the domain
	#	12: Unary exclusive --- the task cannot be assigned this subset of the domain
	#	21: Binary equals --- the tasks need to be assigned the same value
	#	22: Binary not equals --- the tasks cannot be assigned the same value
	#	23: Binary not simultaneous --- the tasks cannot be assigned simultaneously the two values

	# Cosntraint is only called in Graph initialization method. The variables and the values are already created

	def __init__(self, graph, type_of_constraint, list_variables = [], list_values = []):
		self.type = type_of_constraint
		self.variables = list_variables

		if self.type == 0:
			self.values = list_values
			return

		if self.type == 11:
			self.values = [0]*len(graph.values)
			for val_index, possible_val in enumerate(graph.values):
				for constraint_val in list_values:
					if possible_val == constraint_val:
						self.values[val_index] = 1

		elif self.type == 12:
			self.values = [1]*len(graph.values)
			for val_index, possible_val in enumerate(graph.values):
				for constraint_val in list_values:
					if possible_val == constraint_val:
						self.values[val_index] = 0 	

		elif self.type == 21:
			self.values = [[0 for x in range(len(graph.values))] for y in range(len(graph.values))]
			for i in range(0,len(graph.values)):
				self.values[i][i] = 1

		elif self.type == 22:
			self.values = [[1 for x in range(len(graph.values))] for y in range(len(graph.values))]
			for i in range(0,len(graph.values)):
				self.values[i][i] = 0


		elif self.type == 23:
			self.values = [[1 for x in range(len(graph.values))] for y in range(len(graph.values))]
			for val_index_1, possible_val_1 in enumerate(graph.values):
				for val_index_2, possible_val_2 in enumerate(graph.values):
					if ((possible_val_1 == list_values[0] and possible_val_2 == list_values[1]) or
					(possible_val_1 == list_values[1] and possible_val_2 == list_values[0])):
						self.values[val_index_1][val_index_2] = 0

		else:
			assert False, "Constraint init: type of constraint not known"

	def __repr__(self):
		return "Constraint({0}, {1}, {2})".format(self.type, self.variables, self.values)

	def __str__(self):
		string = "\nCosntraint:\n"
		string += "Type:\n{0}\n".format(self.type)
		string += "Variables:\n{0}\n".format(self.variables)
		string += "Values:\n"
		if self.type/10 == 2:
			for j in range(len(self.values)):
				string += str(self.values[j])
				string += "\n"
		else:
			string += str(self.values)
			string += "\n"
		return "{0}, {1}, {2}".format(self.type, self.variables, self.values)



	def updateBinaryConstraint(self, graph, unaryConstraint):
		assert self.type in [21, 22, 23], "Constraint updateBinaryConstraint: constraint type not in whitelist"

		if unaryConstraint.variables[0] == self.variables[0]:
			for i in range(len(graph.values)):
				for j in range(len(graph.values)):
					self.values[i][j] = (self.values[i][j] and unaryConstraint.values[i])

		elif unaryConstraint.variables[0] == self.variables[1]:
			for i in range(len(graph.values)):
				for j in range(len(graph.values)):
					self.values[i][j] = (self.values[i][j] and unaryConstraint.values[j])

class Graph:

	variables = []
	values = []

	uniform = []
	unaryInclusive = []
	unaryExclusive = []
	binaryEqual = []
	binaryNotEqual = []
	binaryNotSimultaneous = []

	possibleAssignments = []

	constraints = [uniform, unaryInclusive, unaryExclusive, binaryEqual, binaryNotEqual, binaryNotSimultaneous]

	def __str__(self):
		string = "List of variables:\n"
		for var in self.variables:
			string += "{0}\n".format(var.name)

		string += "\nList of values:\n"
		for val in self.values:
			string += "{0}\n".format(val.name)

		string += "\nList of constraints:\n"
		for const in self.constraints:
			string += "{0}\n".format(const)

		return string


	# list_variables = [[var1arg1, var1arg2, ...], [var2arg1,...], ...]
	# list_values = [value1, value2, ...]
	def __init__(self, list_variables, list_values, constraints_deadline = [], constraints_unary_inclusive = [],
					constraints_unary_exclusive = [], constraints_binary_equal = [], constraints_binary_not_equal = [],
					constraints_binary_not_simultaneous = []):

		for var_args in list_variables:
			self.variables.append(Variable(var_args))
		for val in list_values:
			self.values.append(Value(val))
		for var in self.variables:
			self.possibleAssignments.append([var, []])
			for val in self.values:
				self.possibleAssignments[-1][1].append(val)


		self.uniform.append(Constraint(self, 0, self.variables, constraints_deadline))

		self.addUnaryConstraint(0, constraints_unary_inclusive)
		self.addUnaryConstraint(1, constraints_unary_exclusive)

		self.addBinaryConstraint(0, constraints_binary_equal)
		self.addBinaryConstraint(1, constraints_binary_not_equal)
		self.addBinaryConstraint(2, constraints_binary_not_simultaneous)

		for binary_constraint in self.binaryEqual + self.binaryNotEqual + self.binaryNotSimultaneous:
			for unary_constraint in self.unaryInclusive + self.unaryExclusive:
				if unary_constraint.variables[0] in binary_constraint.variables:
					binary_constraint.updateBinaryConstraint(self, unary_constraint)

		self.initializePossibleAssignments()


	def addUnaryConstraint(self,type_of_constraint, list_constraints):
		for constraint in list_constraints:
			constraintVar = -1
			for var in self.variables:
				if var.name == constraint[0]:
					constraintVar = [var]
					break
			assert constraintVar != -1

			constraintValues = []
			for constraint_val in constraint.split( )[1:]:
				for val in self.values:
					if constraint_val == val.name:
						constraintValues.append(val)
						break
			assert len(constraintValues) == len(constraint.split( ))-1

			if type_of_constraint == 0:
				self.unaryInclusive.append(Constraint(self, 11, constraintVar, constraintValues))
			if type_of_constraint == 1:
				self.unaryExclusive.append(Constraint(self, 12, constraintVar, constraintValues))

	def addBinaryConstraint(self, type_of_constraint, list_constraints):
		for constraint in list_constraints:
			constraintVar = []
			for var in self.variables:
				if var.name == constraint.split()[0] or var.name == constraint.split()[1]:
					constraintVar.append(var)
			assert len(constraintVar) == 2

			constraintValues = []
			for constraint_val in constraint.split( )[2:]:
				for val in self.values:
					if constraint_val == val.name:
						constraintValues.append(val)
						break

			assert len(constraintVar) == 2
			assert len(constraintValues) == 0 or len(constraintValues) == 2

			if type_of_constraint == 0:
				self.binaryEqual.append(Constraint(self, 21, constraintVar))
			if type_of_constraint == 1:
				self.binaryNotEqual.append(Constraint(self, 22, constraintVar))
			if type_of_constraint == 2:
				self.binaryNotSimultaneous.append(Constraint(self, 23, constraintVar, constraintValues))

	def initializePossibleAssignments(self):
		# initialize the possible assignment with the initial constraints
		# constraints = [list_constraints_1, list_constraints_2, ...]
		for [var, assignments] in self.possibleAssignments:
			for constraint_list in self.constraints[1:]: #TODO: increment if unary constraints start not at constraints[1]
				for constraint in constraint_list:
					if var not in constraint.variables:
						continue
					elif constraint.type > 9 and constraint.type < 20:
						for i, isPossible in enumerate(constraint.values):
							if not isPossible and self.values[i] in assignments:
								assignments.remove(self.values[i])
					elif constraint.type > 19:
						if var == constraint.variables[0]:
							for i in range(len(constraint.values)):
								isPossible = False
								for j in range(len(constraint.values[0])):
									if constraint.values[i][j] == 1:
										isPossible = True
										break
								if not isPossible and self.values[i] in assignments:
									assignments.remove(self.values[i])
						elif var == constraint.variables[1]:
							for i in range(len(constraint.values[0])):
								isPossible = False
								for j in range(len(constraint.values)):
									if constraint.values[j][i] == 1:
										isPossible = True
										break
								if not isPossible and self.values[i] in assignments:
									assignments.remove(self.values[i])
						else:
							assert False


	def selectVariable(self, assignment):
		# assignment contains variable already assigned
		# return the variable to expand in order of expansion
		# return the variable with the minimum remaining value first
		# if tie, select the one with the most constraints

		minRemainingValues = self.minRemainingValues(self.selectRemainingValues(), assignment)

		self.maxConstraintedValues(minRemainingValues, assignment)
		# remainingValue = [[var, #possible values, #constraints], ...]

		#print sorted(sorted(minRemainingValues, key = lambda x: x[2]), key = lambda y: y[1])

		return sorted(sorted(minRemainingValues, key = lambda x: x[2], reverse = True), key = lambda y: y[1])

		# minRemainingValues is a set of [var, possibleValues]
		# decide between them with the degree heuristic: the most constraint var goes first.
		# simply sort by number of time the variable is present in a binary constraint
		"""
		numberOfConstraints = [0]*len(minRemainingValues)
		for i, [var, minRemVal] in enumerate(minRemainingValues):
			for constraintType in self.constraints[3:]: #TODO: change if there is more than 3 non binary constraints!
				for constraint in constraintType:
					if var in constraint.variables:
						numberOfConstraints[i] += 1
		
		return minRemainingValues[numberOfConstraints.index(max(numberOfConstraints))][0]
		"""

	def maxConstraintedValues(self, setVariables, assignment):
		for i in range(len(setVariables)):
			setVariables[i].append(-1)
		for i, [var, minRemVal, init] in enumerate(setVariables):
			numberOfConstraints = 0
			for constraintType in self.constraints[3:]: #TODO: change if there is more than 3 non binary constraints!
				for constraint in constraintType:
					if var in constraint.variables:
						numberOfConstraints += 1
			setVariables[i][2] = numberOfConstraints
		return setVariables


	def minRemainingValues(self, remainingValues, assignment):
		numberRemainingValues = [sum(x) for x in remainingValues]
		minRemainingValues = []

		for i in range(len(numberRemainingValues)):
			isAssigned = False
			for assignedVariable in assignment:
				if assignedVariable[0] == self.variables[i]:
					isAssigned = True
					break

			if not isAssigned:
				minRemainingValues.append([self.variables[i], numberRemainingValues[i]])
			"""
			if numberRemainingValues[i] < minRemainingValues[0][1]:
				minRemainingValues = [[self.variables[i], numberRemainingValues[i]]]
			elif numberRemainingValues[i] == minRemainingValues[0][1]:
				minRemainingValues.append([self.variables[i], numberRemainingValues[i]])
			"""

		return minRemainingValues

	def selectRemainingValues(self, additionalConstraints = []):

		# return the remaining values for each variable with the up to date constraints
		# the additional constraint act as a single unary inc constraint to simulate the assignment of the variable

		remainingValues = [[1 for x in range(len(self.values))] for y in range(len(self.variables))]


		for list_const in self.constraints + [additionalConstraints]:
			if len(list_const) == 0 or list_const[0].type < 10:
				continue

			for const in list_const:
				if const.type < 20:
					varIndex = self.variables.index(const.variables[0])
					for i in range(len(self.values)):
						remainingValues[varIndex][i] = remainingValues[varIndex][i] and const.values[i]
				else:
					varIndex1 = self.variables.index(const.variables[0])
					varIndex2 = self.variables.index(const.variables[1])
					for i in range(len(self.values)):
						remaining1 = 0
						for j in range(len(self.values)):
							if const.values[i][j] == 1:
								remaining1 = 1
								break
						remaining2 = 0
						for j in range(len(self.values)):
							if const.values[j][i] == 1:
								remaining2 = 1
								break

						remainingValues[varIndex1][i] = remainingValues[varIndex1][i] and remaining1
						remainingValues[varIndex2][i] = remainingValues[varIndex2][i] and remaining2

		#print "remainingValues {0}".format(remainingValues)

		return remainingValues

	def selectValue(self, variable, assignment):
		# least constraining value heuristic:
		# sort the values in order of increment constraints
		# for all the value possible for this variable, count the number of possible values for the other variables
		# and pick the one with the highest minimum


		numberRemainingValues = [-1]*len(self.variables)
		minNumberRemainingValues = []
		for i, val in enumerate(self.possibleAssignments[self.variables.index(variable)][1]):
			minNumberRemainingValues.append([val])
			minNumberRemainingValues[-1].append(self.minRemainingValues(
												self.selectRemainingValues([Constraint(self, 11, [variable], [val])]), 
												assignment
												)[0][1]
												)

		return sorted(minNumberRemainingValues,key = lambda x: x[1])

	def consistentAssignment(self, variable, value, assignment):

		varIndex = self.variables.index(variable)
		valIndex = self.values.index(value)


		for list_const in self.constraints :
			if len(list_const) == 0:
				continue

			for const in list_const:
				if variable not in const.variables:
					continue
				if list_const[0].type == 0:
					length = 0
					for assign in assignment:
						if assign[1] == value:
							length += int(assign[0].args) 						#TODO change if there is no deadline constraint!!
					return int(const.values[0]) > length + int(variable.args)
				if const.type < 20:
					return const.values[valIndex] == 1
				else:
					if variable == const.variables[0]:
						for j in range(len(const.values[0])):
							if const.values[valIndex][j] == 1:
								return True
						return False

					if variable == const.variables[0]:
						for j in range(len(const.values)):
							if const.values[j][valIndex] == 1:
								return True
						return False

		return True

def removeInconsistentValue(graph, arc):
	# arc = [value assigned, value linked, binary constraint, values in order in constraint]
	removed = False
	for possibleAssignment in graph.possibleAssignments:
		if arc[0] == possibleAssignment[0]:
			domain1 = possibleAssignment[1]
			break
	for possibleAssignment in graph.possibleAssignments:
		if arc[1] == possibleAssignment[0]:
			domain2 = possibleAssignment[1]
			break

	for possibleValue1 in domain1:
		satisfied = False
		for possibleValue2 in domain2:
			#if Value1 and Value2 satisfy the constraint then  turn satisfied to True
			if arc[3] == 0:
				if constraint[graph.values.index(possibleValue1)][graph.values.index(possibleValue1)] == 1:
					satisfied = True
					break
			if arc[3] == 1:
				if constraint[graph.values.index(possibleValue2)][graph.values.index(possibleValue1)] == 1:
					satisfied = True
					break
		if not satisfied:
			domain1.remove(possibleValue1)
			removed = True
	return removed


def constraintPropagation(graph, variableAssigned):
	# create the queue of arcs, corresponding to the binary constraints
	queue = []
	for constraint_list in graph.constraints:
		if constraint_list[0].type > 19:
			for constraint in constraint_list:
				if variableAssigned == constraint.variables[0]:
					queue.append([variableAssigned, constraint.variables[1], constraint, 0])
				elif variableAssigned == constraint.variables[1]:
					queue.append([variableAssigned, constraint.variables[0], constraint, 1])

	while len(queue) > 0:
		arc = queue[0]
		del queue[0]
		if removedInconsistentValue(graph, arc):
			for constraint_list in graph.constraints:
				if constraint_list[0].type > 19:
					for constraint in constraint_list:
						if arc[1] == constraint.variables[0]:
							queue.append([arc[1], constraint.variables[1], constraint, 0])
						elif arc[1] == constraint.variables[1]:
							queue.append([arc[1], constraint.variables[0], constraint, 1])


def backtrackingSearch(graph):
	return recursiveBacktracking([], graph)

def recursiveBacktracking(assignment, graph):
	if len(assignment) == len(graph.variables):
		return assignment

	for [var, numRemainVal, numConstr] in graph.selectVariable(assignment):
		print "variable selected: {0}".format(var)
		for [val, minNumb] in graph.selectValue(var, assignment):
			print "test with value {0}".format(val)
			if graph.consistentAssignment(var, val, assignment):
				print "{0} assigned {1} is consistent, test the children".format(var, val)
				assignment.append([var, val])
				result = recursiveBacktracking(assignment, graph)
				if result != False:
					return result
				assignment.remove([var, val])
				print "no solution with {0} assigned to {1}".format(var, val)
			print "{0} assigned {1} is not consistent, test next variable".format(var, val)
		return False




def main():
	if len(sys.argv) != 2:
		print "Usage: python CSP.py {input file}"
		return

	try:
		f = open(sys.argv[1], "r")
	except Exception:
		pass

	lines = []
	for line in f.readlines():
		lines.append(line[:-1])


	# input list in order [variables, values, deadline constraints, unary inclusive, unary exclusive, binary equals,
	#						binary not equals, binary not simultaneous]
	input_list = []
	for line in lines:
		if re.match("#####*", line):
			input_list.append([])
		else:
			input_list[-1].append(line)

	print input_list

	graph = Graph(input_list[0], input_list[1], input_list[2], input_list[3], input_list[4], input_list[5],
					input_list[6], input_list[7])


	solution =  backtrackingSearch(graph)
	if solution:
		print solution
	else:
		print "no solution"


if __name__ == '__main__':
	main()

