import sys
import re

class Variable:

	def __init__(self, list_args):
		self.name = list_args[0]
		self.args = list_args[1:]
		

class Value:

	def __init__(self, n):
		self.name = n


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

		if self.type == 0:
			self.list_values = list_values
			return

		self.variables = list_variables

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
			self.values = [[0]*len(graph.values)]*len(graph.values)
			for i in range(0,len(graph.values)):
				self.values[i][i] == 1

		elif self.type == 22:
			self.values = [[1]*len(graph.values)]*len(graph.values)
			for i in range(0,len(graph.values)):
				self.values[i][i] == 0

		elif self.type == 23:
			self.values = [[1]*len(graph.values)]*len(graph.values)
			for val_index_1, possible_val_1 in enumerate(graph.values):
				for val_index_2, possible_val_2 in enumerate(graph.values):
					if ((possible_val_1 == list_values[0] and possible_val_2 == list_values[1]) or
					(possible_val_1 == list_values[1] and possible_val_2 == list_values[0])):
						self.values[val_index_1][val_index_2] == 0

		else:
			assert False, "Constraint init: type of constraint not known"


	def __str__(self):
		return "{0}, {1}, {2}".format(self.type, self.variables, self.values)


	def updateBinaryConstraint(self, graph, unaryConstraint):
		assert self.type in [21, 22, 23], "Constraint updateBinaryConstraint: constraint type not in whitelist"

		index_value = graph.variables.index(unaryConstraint.variables)

		if unaryConstraint.variables == self.variables[0]:
			for i in range(len(graph.values)):
				self.values[index_value][i] = self.values[index_value][i] and unaryConstraint.values[i]

		if unaryConstraint.variables == self.variables[1]:
			for i in range(len(graph.values)):
				self.values[i][index_value] = self.values[i][index_value] and unaryConstraint.values[i]

class Graph:

	variables = []
	values = []

	unaryInclusive = []
	unaryExclusive = []
	binaryEqual = []
	binaryNotEqual = []
	binaryNotSimultaneous = []

	# list_variables = [[var1arg1, var1arg2, ...], [var2arg1,...], ...]
	# list_values = [value1, value2, ...]
	def __init__(self, list_variables, list_values, constraints_deadline = -1, constraints_unary_inclusive = [],
					constraints_unary_exclusive = [], constraints_binary_equal = [], constraints_binary_not_equal = [],
					constraints_binary_not_simultaneous = []):

		for var_args in list_variables:
			self.variables.append(Variable(var_args))
		for val in list_values:
			self.values.append(Value(val))

		self.deadline = constraints_deadline

		self.addUnaryConstraint(0, constraints_unary_inclusive)
		self.addUnaryConstraint(1, constraints_unary_exclusive)

		self.addBinaryConstraint(0, constraints_binary_equal)
		self.addBinaryConstraint(1, constraints_binary_not_equal)
		self.addBinaryConstraint(2, constraints_binary_not_simultaneous)

		for binary_constraint in self.binaryEqual + self.binaryNotEqual + self.binaryNotSimultaneous:
			for unary_constraint in self.unaryInclusive + self.unaryExclusive:
				if unary_constraint.variables in binary_constraint.variables:
					binary_constraint.updateBinaryConstraint(self, unary_constraint)

	def addUnaryConstraint(self,type_of_constraint, list_constraints):
		for constraint in list_constraints:
			constraintVar = -1
			for var in self.variables:
				if var.name == constraint[0]:
					constraintVar = var
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


if __name__ == '__main__':
	main()

