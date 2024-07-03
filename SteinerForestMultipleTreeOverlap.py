import pandas as pd
import argparse
import gurobipy

class GurobiData:
	def __init__(self, args):

		df_connected_edge = pd.read_csv(args.data_path + '/connected_edge.csv', header=None)
		df_unconnected_edge = pd.read_csv(args.data_path + '/unconnected_edge.csv', header=None)
		df_component_number_per_line = pd.read_csv(args.data_path + '/component_number_per_line.csv', header=None)
		df_margin_and_radius = pd.read_csv(args.data_path + '/margin_and_radius.csv', header=None)
		df_component_position = pd.read_csv(args.data_path + '/component_position.csv', header=None)
		data_connected_edge = df_connected_edge.values.tolist()
		data_unconnected_edge = df_unconnected_edge.values.tolist()
		data_component_number_per_line = df_component_number_per_line.values.tolist()
		data_margin_and_radius = df_margin_and_radius.values.tolist()
		data_component_position = df_component_position.values.tolist()
		
		self.__margin = data_margin_and_radius[0][0::2]
		self.__radius = data_margin_and_radius[0][1::2]
		
		component_number_per_line = data_component_number_per_line[0]
		self.__component_position_per_line = []
		pre_number = 0
		for i in range(len(component_number_per_line)):
			component_position = data_component_position[pre_number:pre_number + component_number_per_line[i]]
			pre_number += component_number_per_line[i]
			self.__component_position_per_line.append(component_position)
		for i in range(len(self.__component_position_per_line)):
			for j in range(len(self.__component_position_per_line[i])):
				self.__component_position_per_line[i][j] = self.__point_lable(self.__component_position_per_line[i][j])
		
		self.__edges = {}
		index = 0
		for position in data_connected_edge:
			one_point = self.__point_lable(position[:3])
			two_point = self.__point_lable(position[3:])
			self.__edges[index] = (one_point, two_point)
			self.__edges[index + 1] = two_point, one_point
			index += 2
		
		if args.is_connected == "connected":
			for position in data_unconnected_edge:
				one_point = self.__point_lable(position[:3])
				two_point = self.__point_lable(position[3:])
				self.__edges[index] = one_point, two_point
				self.__edges[index + 1] = two_point, one_point
				index += 2
				
		
		self.__edge_to_index = []
		self.__index_to_edge = []
		for i in range(self.get_line_number()):
			dictionary_edge_to_index = {}
			dictionary_index_to_edge = {}
			index = 0
			for j in range(len(self.__edges)):
				pre_point = self.__edges[j][0]
				next_point = self.__edges[j][1]
				key = True
				for k in range(self.get_line_number()):
					if k == i:
						continue
					for l in range(len(self.__component_position_per_line[k])):
						if pre_point == self.__component_position_per_line[k][l] or next_point == self.__component_position_per_line[k][l]:
							key = False
							break
					if not key:
						break
				if key:
					dictionary_edge_to_index[pre_point, next_point] = index
					dictionary_index_to_edge[index] = (pre_point, next_point)
					index += 1
			self.__edge_to_index.append(dictionary_edge_to_index)
			self.__index_to_edge.append(dictionary_index_to_edge)
		
		
		self.__adjacency_edge_out_degree = []
		self.__adjacency_edge_in_degree = []
		for i in range(len(self.__component_position_per_line)):
			dictionary_adjacency_edge_out_degree = {}
			dictionary_adjacency_edge_in_degree = {}
			for j in range(len(self.__index_to_edge[i])):
				pre_point = self.__index_to_edge[i][j][0]
				if pre_point not in dictionary_adjacency_edge_out_degree:
					dictionary_adjacency_edge_out_degree[pre_point] = []
				dictionary_adjacency_edge_out_degree[pre_point].append(j)
				
				next_point = self.__index_to_edge[i][j][1]
				if next_point not in dictionary_adjacency_edge_in_degree:
					dictionary_adjacency_edge_in_degree[next_point] = []
				dictionary_adjacency_edge_in_degree[next_point].append(j)
				
			self.__adjacency_edge_out_degree.append(dictionary_adjacency_edge_out_degree)
			self.__adjacency_edge_in_degree.append(dictionary_adjacency_edge_in_degree)
		
		self.__all_in_edge = {}
		for i in range(self.get_point_number()):
			all_in_edges = []
			for j in range(self.get_line_number()):
				if i in self.get_adjacency_edge_in_degree()[j].keys():
					edges = self.get_adjacency_edge_in_degree()[j][i]
					for k in edges:
						all_in_edges.append((j, k))
			self.__all_in_edge[i] = all_in_edges
	
	def __point_lable(self, position):
		return position[0] + position[1] * args.length + position[2] * args.length * args.width
	
	def get_component_position_per_line(self):
		return self.__component_position_per_line
	
	def get_edge_to_index(self):
		return self.__edge_to_index
	
	def get_adjacency_edge_out_degree(self):
		return self.__adjacency_edge_out_degree
	
	def get_adjacency_edge_in_degree(self):
		return self.__adjacency_edge_in_degree
	
	def get_line_number(self):
		return len(self.__component_position_per_line)
	
	def get_edge_number(self, line_index):
		return len(self.__edge_to_index[line_index])
	
	def get_point_number(self):
		return args.length * args.width * 2
	
	def get_first_component_per_line(self, line_index):
		return self.__component_position_per_line[line_index][0]
	
	def get_residual_component_per_line(self, line_index):
		return self.__component_position_per_line[line_index][1:]
	
	def get_index_to_edge(self):
		return self.__index_to_edge
	
	def get_all_in_edge(self):
		return self.__all_in_edge
	
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='manual to this script')
	parser.add_argument('--high', type=int, default=2)
	parser.add_argument("--length", type=int, default=16)
	parser.add_argument("--width", type=int, default=16)
	parser.add_argument("--data_path", type=str, default="./data/instance1")
	parser.add_argument("--is_connected", type=str, default="connected")
	args = parser.parse_args()
	
	data = GurobiData(args)
	
	MODEL = gurobipy.Model()
	
	x = {}
	for i in range(data.get_line_number()):
		for j in range(data.get_edge_number(i)):
			x[i, j] = MODEL.addVar(vtype=gurobipy.GRB.BINARY)

	for i in range(data.get_line_number()):
		first_component_position = data.get_first_component_per_line(i)
		adjacency_edge = data.get_adjacency_edge_out_degree()[i][first_component_position]
		MODEL.addConstr(gurobipy.quicksum([x[i, j] for j in adjacency_edge]) >= 1)
		
	for i in range(data.get_line_number()):
		residual_component_position = data.get_residual_component_per_line(i)
		for j in residual_component_position:
			adjacency_edge = data.get_adjacency_edge_in_degree()[i][j]
			MODEL.addConstr(gurobipy.quicksum([x[i, k] for k in adjacency_edge]) == 1)
	
	for i in range(data.get_line_number()):
		points = data.get_adjacency_edge_in_degree()[i].keys()
		components = data.get_component_position_per_line()[i]
		for point in points:
			if point in components:
				continue
			out_point = data.get_adjacency_edge_out_degree()[i][point]
			in_point = data.get_adjacency_edge_in_degree()[i][point]
			MODEL.addConstr(gurobipy.quicksum(x[i, j] for j in out_point) >= gurobipy.quicksum(x[i, j] for j in in_point))
			MODEL.addConstr(gurobipy.quicksum(x[i, j] for j in out_point) <= 100 * gurobipy.quicksum(x[i, j] for j in in_point))
	
	for i in range(data.get_point_number()):
		MODEL.addConstr(gurobipy.quicksum(x[j, k] for j, k in data.get_all_in_edge()[i]) <= 1)
	
	u = {}
	for i in range(data.get_line_number()):
		for j in range(data.get_point_number()):
			u[i, j] = MODEL.addVar(lb=0, ub=data.get_point_number() - 1, vtype=gurobipy.GRB.INTEGER)
	
	
	for i in range(data.get_line_number()):
		edges = data.get_index_to_edge()[i]
		for j in range(data.get_edge_number(i)):
			pre_position = edges[j][0]
			next_position = edges[j][1]
			MODEL.addConstr(u[i, pre_position] - u[i, next_position] + data.get_point_number() * x[i, j] <= data.get_point_number() - 1)
	
	for i in range(data.get_line_number()):
		position = data.get_first_component_per_line(i)
		MODEL.addConstr(u[i, position] == 0)
		
	MODEL.setObjective(gurobipy.quicksum([x[i, j] for i in range(data.get_line_number()) for j in range(data.get_edge_number(i))]), gurobipy.GRB.MINIMIZE)
	MODEL.optimize()