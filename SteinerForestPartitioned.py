import pandas as pd
import argparse
import copy
import time
import random
import numpy as np
import math


class graph_manage():
	def __init__(self, parent_graph):
		self.parent_graph = parent_graph
		self.child_path = []
		self.child_path_index = []
	
	def add_path(self, index, path):
		self.child_path_index.append(index)
		self.child_path.append(path)
	
	def delete_graph(self):
		return self.child_path_index.pop(0), self.child_path.pop(0)
	
	def get_residual_graph(self):
		parent_points = self.parent_graph.get_points()
		parent_adjacency_point = copy.deepcopy(self.parent_graph.get_adjacency_point())
		child_points = set()
		for i in self.child_path:
			child_points.update(i)
		points = parent_points - child_points
		
		for point in child_points:
			if point in parent_adjacency_point:
				adjacency_point = parent_adjacency_point[point]
				for i in adjacency_point:
					parent_adjacency_point[i].remove(point)
				del parent_adjacency_point[point]
		
		residual_graph = graph(points=points, adjacency_point=parent_adjacency_point)
		return residual_graph

class graph():
	parent_point_length = 0
	def __init__(self, points, adjacency_point):
		self.__points = points
		self.__adjacency_point = adjacency_point
	
	@staticmethod
	def set_parent_point_length(value):
		graph.parent_point_length = value
	
	def get_points(self):
		return self.__points
	
	def get_adjacency_point(self):
		return self.__adjacency_point
	
	def is_connected(self, components):
		for i in components:
			if i not in self.__points:
				return False
		flag = {}
		for i in self.__points:
			flag[i] = -1
		
		visit = [components[0]]
		flag[components[0]] = 0
		while len(visit) != 0:
			current_point = visit.pop(0)
			next_points = self.__adjacency_point[current_point]
			for i in next_points:
				if flag[i] == -1:
					flag[i] = flag[current_point] + 1
					visit.append(i)
		for i in components:
			if flag[i] == -1:
				return False
		return True
	
	def get_distance(self, component):
		flag = np.full(self.parent_point_length, -1)
		visit = [component]
		flag[component] = 0
		while len(visit) != 0:
			current_point = visit.pop(0)
			next_points = self.__adjacency_point[current_point]
			for i in next_points:
				if flag[i] == -1:
					flag[i] = flag[current_point] + 1
					visit.append(i)
		return flag
	
def init_data():
	data_connected_edge = pd.read_csv(args.data_path + '/connected_edge.csv', header=None).values.tolist()
	data_unconnected_edge = pd.read_csv(args.data_path + '/unconnected_edge.csv', header=None).values.tolist()
	data_component_number_per_line = pd.read_csv(args.data_path + '/component_number_per_line.csv', header=None).values.tolist()
	data_margin_and_radius = pd.read_csv(args.data_path + '/margin_and_radius.csv', header=None).values.tolist()
	data_component_position = pd.read_csv(args.data_path + '/component_position.csv', header=None).values.tolist()
	
	point_dir = {}
	adjacency_point = {}
	index = 0
	for position in data_connected_edge:
		if (position[0], position[1], position[2]) not in point_dir:
			point_dir[(position[0], position[1], position[2])] = index
			index += 1
		if (position[3], position[4], position[5]) not in point_dir:
			point_dir[(position[3], position[4], position[5])] = index
			index += 1
		
		if point_dir[position[0], position[1], position[2]] not in adjacency_point:
			adjacency_point[point_dir[position[0], position[1], position[2]]] = set()
		adjacency_point[point_dir[position[0], position[1], position[2]]].add(
			point_dir[(position[3], position[4], position[5])])
		
		if point_dir[position[3], position[4], position[5]] not in adjacency_point:
			adjacency_point[point_dir[position[3], position[4], position[5]]] = set()
		adjacency_point[point_dir[position[3], position[4], position[5]]].add(
			point_dir[(position[0], position[1], position[2])])
	
	if args.is_connected == "connected":
		for position in data_unconnected_edge:
			if (position[0], position[1], position[2]) not in point_dir:
				point_dir[(position[0], position[1], position[2])] = index
				index += 1
			if (position[3], position[4], position[5]) not in point_dir:
				point_dir[(position[3], position[4], position[5])] = index
				index += 1
			
			if point_dir[position[0], position[1], position[2]] not in adjacency_point:
				adjacency_point[point_dir[position[0], position[1], position[2]]] = set()
			adjacency_point[point_dir[position[0], position[1], position[2]]].add(
				point_dir[(position[3], position[4], position[5])])
			
			if point_dir[position[3], position[4], position[5]] not in adjacency_point:
				adjacency_point[point_dir[position[3], position[4], position[5]]] = set()
			adjacency_point[point_dir[position[3], position[4], position[5]]].add(
				point_dir[(position[0], position[1], position[2])])
	
	points = set([i for i in range(len(point_dir))])
	graph.set_parent_point_length(len(point_dir))
	total_graph = graph(adjacency_point=adjacency_point, points=points)
	
	component_position_per_line = []
	pre_number = 0
	for i in range(len(data_component_number_per_line[0])):
		component_position = data_component_position[pre_number:pre_number + data_component_number_per_line[0][i]]
		pre_number += data_component_number_per_line[0][i]
		component_position_per_line.append(component_position)
	for i in range(len(component_position_per_line)):
		for j in range(len(component_position_per_line[i])):
			component_position_per_line[i][j] = point_dir[component_position_per_line[i][j][0], component_position_per_line[i][j][1], component_position_per_line[i][j][2]]
	return total_graph, component_position_per_line

def get_convergence_point(components_flag):
	index_number = int(math.pow(len(components_flag[0]), 0.5) / 2)
	while True:
		index = random.sample([i for i in range(len(components_flag[0]))], index_number)
		total_distance = np.sum([components_flag[i][index] for i in range(len(components_flag))], axis=0)
		min_index = np.argmin(total_distance)
		if total_distance[min_index] > 0:
			break
	return index[min_index], total_distance[min_index]

def get_child_path(graph, flag, convergence_point):
	adjacency_point = graph.get_adjacency_point()
	path = set()
	current_point = convergence_point
	path.add(current_point)
	while flag[current_point] != 0:
		next_points = adjacency_point[current_point]
		points = []
		for point in next_points:
			if flag[point] == flag[current_point] - 1:
				points.append(point)
		current_point = random.choice(points)
		path.add(current_point)
	return path

def get_adjacent_point(graph, points):
	adjacent_point = {}
	parent_adjacent_point = graph.get_adjacency_point()
	for i in points:
		next_points = parent_adjacent_point[i]
		temp = set()
		for j in next_points:
			if j in points:
				temp.add(j)
		adjacent_point[i] = temp
	return adjacent_point
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='manual to this script')
	parser.add_argument('--high', type=int, default=2)
	parser.add_argument("--length", type=int, default=128)
	parser.add_argument("--width", type=int, default=128)
	parser.add_argument("--data_path", type=str, default="./data/instance3")
	parser.add_argument("--is_connected", type=str, default="connected")
	args = parser.parse_args()
	
	parent_graph, component_position_per_line = init_data()
	graph_manage = graph_manage(parent_graph)
	
	task_list = [i for i in range(len(component_position_per_line))]
	
	current_graph = parent_graph
	while len(task_list) > 0:
		print(len(task_list))
		current_task = task_list.pop(0)
		flags = []
		for component_position in range(len(component_position_per_line[current_task])):
			flag = current_graph.get_distance(component_position_per_line[current_task][component_position])
			flags.append(flag)
		convergence_point, _ = get_convergence_point(flags)
		path = set()
		for flag in flags:
			path.update(get_child_path(current_graph, flag, convergence_point))
		graph_manage.add_path(current_task, path)
		while True:
			current_graph = graph_manage.get_residual_graph()
			connected = True
			for i in task_list:
				connected *= current_graph.is_connected(component_position_per_line[i])
				if not connected:
					break
			if connected:
				break
			else:
				task_index, _ = graph_manage.delete_graph()
				task_list.append(task_index)
			