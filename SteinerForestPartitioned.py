import pandas as pd
import argparse
import copy
import time
import random
import numpy as np
import math
import multiprocessing

class GraphManage():
	def __init__(self, points, adjacency_point, component_position_per_line):
		self.parent_graph = Graph(points=points, adjacency_point=adjacency_point)
		self.child_path = []
		self.child_path_index = []
		self.component_position_per_line = component_position_per_line
		self.task_list = [i for i in range(len(component_position_per_line))]
	
	def add_path(self, index, path):
		self.child_path_index.append(index)
		self.child_path.append(path)
	
	def delete_path(self):
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
		
		residual_graph = Graph(points=points, adjacency_point=parent_adjacency_point)
		return residual_graph

	def get_edges_number(self):
		return sum([len(i) for i in self.child_path]) - len(self.child_path)
		
class Graph():
	parent_point_length = 0
	def __init__(self, points, adjacency_point):
		self.__points = points
		self.__adjacency_point = adjacency_point
	
	@staticmethod
	def set_parent_point_length(value):
		Graph.parent_point_length = value
	
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
	
def get_flag(graph, component):
	flag = np.full(graph.parent_point_length, -1)
	visit = [component]
	flag[component] = 0
	while len(visit) != 0:
		current_point = visit.pop(0)
		next_points = graph.get_adjacency_point()[current_point]
		for i in next_points:
			if flag[i] == -1:
				flag[i] = flag[current_point] + 1
				visit.append(i)
	# print(flag)
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
	Graph.set_parent_point_length(len(point_dir))
	total_graph = Graph(adjacency_point=adjacency_point, points=points)
	
	component_position_per_line = []
	pre_number = 0
	for i in range(len(data_component_number_per_line[0])):
		component_position = data_component_position[pre_number:pre_number + data_component_number_per_line[0][i]]
		pre_number += data_component_number_per_line[0][i]
		component_position_per_line.append(component_position)
	for i in range(len(component_position_per_line)):
		for j in range(len(component_position_per_line[i])):
			component_position_per_line[i][j] = point_dir[component_position_per_line[i][j][0], component_position_per_line[i][j][1], component_position_per_line[i][j][2]]
	return points, adjacency_point, component_position_per_line

#同一树中，多个子线路的汇聚点
#components_flag表示各个子线的距离
def get_convergence_point(components_flag, graph):
	point_list = get_point_list(graph)
	index_number = int(math.pow(len(point_list), 0.5) / 2)
	index = random.sample(point_list, index_number)
	total_distance = np.sum([components_flag[i][index] for i in range(len(components_flag))], axis=0)
	min_index = np.argmin(total_distance)
	return index[min_index], total_distance[min_index]

#从图中得到点的列表
def get_point_list(graph):
	return [i for i in graph.get_points()]
#找一条子路
#flag表示子路
#graph表示图
#convergence_point表示汇聚点，也就是出发点
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

def get_path(graph_manage):
	task_list = graph_manage.task_list
	component_position_per_line = graph_manage.component_position_per_line
	
	current_graph = graph_manage.get_residual_graph()
	for i in range(len(task_list)):
		current_task = task_list.pop(0)
		if current_graph.is_connected(component_position_per_line[current_task]):
			path = get_one_path(current_graph, component_position_per_line[current_task])
			graph_manage.add_path(current_task, path)
			current_graph = graph_manage.get_residual_graph()
		else:
			task_list.append(current_task)
	return graph_manage
	
def get_path_format(points, adjacency_point, component_position_per_line):
	graph_manage = GraphManage(adjacency_point=adjacency_point, points=points, component_position_per_line=component_position_per_line)
	return get_path(graph_manage)

def get_path_mutiprocesing(points, adjacency_point, component_position_per_line, run_number):
	pool = multiprocessing.Pool()
	results = []
	for i in range(run_number):
		results.append(pool.apply_async(get_path_format, args=(points, adjacency_point, component_position_per_line)))
	pool.close()
	pool.join()
	max_length = 0
	max_result = 0
	for result in results:
		if max_length < len(result.get().child_path):
			max_length = len(result.get().child_path)
			max_result = result.get()
	return max_result

def get_flag_format(points, adjacency_point, component):
	graph = Graph(adjacency_point=adjacency_point, points=points)
	return get_flag(graph, component)

def get_flag_mutiprocessing(graph, components_position):
	processing_number = min(multiprocessing.cpu_count(), len(components_position))
	pool = multiprocessing.Pool(processes=processing_number)
	results = []
	for i in range(len(components_position)):
		results.append(pool.apply_async(get_flag_format, args=(graph.get_points(), graph.get_adjacency_point(), components_position[i])))
	pool.close()
	pool.join()
	flags = []
	for result in results:
		flags.append(result.get())
	return flags

def get_child_path_format(points, adjacency_point, flag, convergence_point):
	graph = Graph(adjacency_point=adjacency_point, points=points)
	points = get_child_path(graph, flag, convergence_point)
	return points

def get_child_path_mutiprocessing(graph, flags, convergence_point):
	process_number = min(multiprocessing.cpu_count(), len(flags))
	pool = multiprocessing.Pool(processes=process_number)
	results = []
	for flag in flags:
		results.append(pool.apply_async(get_child_path_format, args=(graph.get_points(), graph.get_adjacency_point(), flag, convergence_point)))
	pool.close()
	pool.join()
	path = set()
	for result in results:
		path.update(result.get())
	return path
	
	
def get_one_path(graph, components_position):
	flags = []
	for i in range(len(components_position)):
		flag = get_flag(graph, components_position[i])
		flags.append(flag)
	
	# flags = get_flag_mutiprocessing(graph, components_position)
	convergence_point, _ = get_convergence_point(flags, graph)
	# path = get_child_path_mutiprocessing(graph, flags, convergence_point)
	path = set()
	for flag in flags:
		points = get_child_path(graph, flag, convergence_point)
		path.update(points)
	return path
	
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='manual to this script')
	parser.add_argument("--data_path", type=str, default="./data/instance3")
	parser.add_argument("--is_connected", type=str, default="connected")
	args = parser.parse_args()

	points, adjacency_point, component_position_per_line = init_data()
	graph_manage = GraphManage(points, adjacency_point, component_position_per_line)
	
	task_list = graph_manage.task_list
	get_path(graph_manage)
	while len(task_list) > 0:
		print(task_list)
		index, _ = graph_manage.delete_path()
		task_list.append(index)
		
		for i in range(len(graph_manage.child_path)):
			child_path_index, _ = graph_manage.delete_path()
			residual_graph = graph_manage.get_residual_graph()
			path = get_one_path(residual_graph, component_position_per_line[child_path_index])
			graph_manage.add_path(child_path_index, path)
		get_path(graph_manage)
	
	print(graph_manage.get_edges_number())

	
	print(len(graph_manage.task_list))
	print(len(task_list))
	print(len(graph_manage.child_path_index))
	print(len(graph_manage.child_path))
	paths = graph_manage.child_path
	for i in range(len(paths)):
		for j in range(i + 1, len(paths)):
			if len(paths[i] & paths[j]) > 0:
				print("fail")
			else:
				print("success")