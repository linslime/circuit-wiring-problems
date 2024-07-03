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
		
		self.__index_to_edge = {}
		self.__edge_to_index = {}
		index = 0
		for position in data_connected_edge:
			one_point = self.__point_lable(position[:3])
			two_point = self.__point_lable(position[3:])
			self.__index_to_edge[index] = one_point, two_point
			self.__edge_to_index[one_point, two_point] = index
			self.__index_to_edge[index + 1] = two_point, one_point
			self.__edge_to_index[two_point, one_point] = index + 1
			index += 2
		
		if args.is_connected == "connected":
			for position in data_unconnected_edge:
				one_point = self.__point_lable(position[:3])
				two_point = self.__point_lable(position[3:])
				self.__index_to_edge[index] = one_point, two_point
				self.__edge_to_index[one_point, two_point] = index
				self.__index_to_edge[index + 1] = two_point, one_point
				self.__edge_to_index[two_point, one_point] = index + 1
				index += 2
		
		self.__point_to_out_edge = {}
		self.__point_to_in_edge = {}
		for i in range(len(self.__index_to_edge)):
			pre_point = self.__index_to_edge[i][0]
			next_point = self.__index_to_edge[i][1]
			
			if pre_point not in self.__point_to_out_edge:
				self.__point_to_out_edge[pre_point] = []
			self.__point_to_out_edge[pre_point].append(i)
			
			if next_point not in self.__point_to_in_edge:
				self.__point_to_in_edge[next_point] = []
			self.__point_to_in_edge[next_point].append(i)
		
		self.__other_point = self.__point_to_out_edge.keys()
		for i in range(self.get_line_number()):
			self.__other_point = self.__other_point - set(self.__component_position_per_line[i])
		
		self.__in_component_edge = set(
			[self.__point_to_in_edge[self.__component_position_per_line[i][j]][k] for i in range(self.get_line_number())
			 for j in range(len(self.__component_position_per_line[i])) for k in
			 range(len(self.__point_to_in_edge[self.__component_position_per_line[i][j]]))])
		self.__other_edge = set([i for i in range(self.get_edge_number())]) - self.__in_component_edge
	
	def __point_lable(self, position):
		return position[0] + position[1] * args.length + position[2] * args.length * args.width
	
	def get_other_point(self):
		return self.__other_point
	
	def get_point_to_out_edge(self):
		return self.__point_to_out_edge
	
	def get_point_to_in_edge(self):
		return self.__point_to_in_edge
	
	def get_index_to_edge(self):
		return self.__index_to_edge
	
	def get_edge_to_index(self):
		return self.__edge_to_index
	
	def get_line_number(self):
		return len(self.__component_position_per_line)
	
	def get_edge_number(self):
		return len(self.__edge_to_index)
	
	def get_point_number(self):
		return args.length * args.width * args.high
	
	def get_first_component_per_line(self, line_index):
		return self.__component_position_per_line[line_index][0]
	
	def get_residual_component_per_line(self, line_index):
		return self.__component_position_per_line[line_index][1:]
	
	def get_all_component_per_line(self, line_index):
		return self.__component_position_per_line[line_index]
	
	def get_index_to_edge(self):
		return self.__index_to_edge
	
	def get_in_component_edge(self):
		return self.__in_component_edge
	
	def get_other_edge(self):
		return self.__other_edge


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
	
	x = MODEL.addVars(data.get_edge_number(), vtype=gurobipy.GRB.BINARY)
	
	for i in range(data.get_line_number()):
		first_component = data.get_first_component_per_line(i)
		out_edges = data.get_point_to_out_edge()[first_component]
		MODEL.addConstr(gurobipy.quicksum(x[j] for j in out_edges) >= 1)

	for i in range(data.get_line_number()):
		residual_components = data.get_residual_component_per_line(i)
		for residual_component in residual_components:
			in_edges = data.get_point_to_in_edge()[residual_component]
			MODEL.addConstr(gurobipy.quicksum(x[j] for j in in_edges) == 1)
	
	for i in data.get_other_point():
		out_edges = data.get_point_to_out_edge()[i]
		in_edges = data.get_point_to_in_edge()[i]
		MODEL.addConstr(gurobipy.quicksum(x[j] for j in out_edges) >= gurobipy.quicksum(x[j] for j in in_edges))
		MODEL.addConstr(gurobipy.quicksum(x[j] for j in out_edges) <= 10 * gurobipy.quicksum(x[j] for j in in_edges))
	
	u = MODEL.addVars(data.get_point_number(), lb=0, ub=data.get_point_number() * data.get_line_number(), vtype=gurobipy.GRB.INTEGER)
	for i in range(data.get_line_number()):
		first_component = data.get_first_component_per_line(i)
		MODEL.addConstr(u[first_component] == i * data.get_point_number())
		
		residual_components = data.get_residual_component_per_line(i)
		for residual_component in residual_components:
			MODEL.addRange(u[residual_component], i * data.get_point_number() + 1, (i + 1) * data.get_point_number() - 1)
	for i in range(data.get_edge_number()):
		pre_point = data.get_index_to_edge()[i][0]
		next_point = data.get_index_to_edge()[i][1]
		MODEL.addConstr((x[i] == 1) >> (u[pre_point] + 1 == u[next_point]))
	
	MODEL.setObjective(gurobipy.quicksum(x[i] for i in range(data.get_edge_number())), gurobipy.GRB.MINIMIZE)
	MODEL.setParam("MIPFocus", 1)
	MODEL.optimize()



