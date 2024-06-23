import pandas as pd
import copy
import random
import argparse

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument("--length", type=int, default=16)
parser.add_argument("--width", type=int, default=16)
parser.add_argument("--p", type=float, default=0.975)
parser.add_argument("--max_search_length", type=int, default=2000)
parser.add_argument("--data_path", type=str, default="./data/instance1")
parser.add_argument("--is_connected", type=str, default="connected")
args = parser.parse_args()

# 全局变量
B = {}
margin = []
radius = []

line_point = []

point = [1 for i in range(2 * args.length * args.width)]
pointtemp = []


# 读数据
def read():
	df1 = pd.read_csv(args.data_path + '/connected_edge.csv', header=None)
	df2 = pd.read_csv(args.data_path + '/unconnected_edge.csv', header=None)
	df3 = pd.read_csv(args.data_path + '/margin_and_radius.csv', header=None)
	df4 = pd.read_csv(args.data_path + '/component_position.csv', header=None)
	df5 = pd.read_csv(args.data_path + '/component_number_per_line.csv', header=None)
	data1 = df1.values.tolist()
	data2 = df2.values.tolist()
	data3 = df3.values.tolist()
	data4 = df4.values.tolist()
	data5 = df5.values.tolist()
	for i in data1:
		one = pointnumber(i[:3])
		two = pointnumber(i[3:])
		B[one, two] = 1
		B[two, one] = 1
	
	if args.is_connected == "connected":
		for i in data2:
			one = pointnumber(i[:3])
			two = pointnumber(i[3:])
			B[one, two] = 1
			B[two, one] = 1
	else:
		for i in data2:
			one = pointnumber(i[:3])
			two = pointnumber(i[3:])
			B[one, two] = 0
			B[two, one] = 0
	
	linetemp = []
	for i in range(len(data5[0])):
		linetemp.append(data5[0][i])
	margin = data3[0][0::2]
	radius = data3[0][1::2]
	for i in range(len(margin)):
		margin[i] = int(margin[i])
		radius[i] = int(radius[i])
		linetemp[i] = int(linetemp[i])
	
	for i in data4:
		point[pointnumber(i)] = 0
	temp = 0
	for i in range(len(linetemp)):
		list = [i] + data4[temp:temp + linetemp[i]]
		temp += linetemp[i]
		line_point.append(list)


# 点号
def pointnumber(list):
	return list[0] + list[1] * args.length + list[2] * args.length * args.width


# 曼哈顿距离
def Manhattandistance(list1, list2):
	return sum([abs(list1[i] - list2[i]) for i in range(3)])


# 求出最小距离目标
def getmindistance(list1, list2):
	mindistance = 100000000000000
	mindistancepoint = []
	for i in range(len(list2)):
		distance = Manhattandistance(list1, list2[i])
		if distance < mindistance:
			mindistancepoint = list2[i]
			mindistance = distance
	return [mindistancepoint, mindistance]


# 寻找临近点
def getnearpoint(list):
	edge = []
	if list[0] - 1 >= 0:
		edge.append([list[0] - 1, list[1], list[2]])
	if list[0] + 1 <= args.length - 1:
		edge.append([list[0] + 1, list[1], list[2]])
	if list[1] - 1 >= 0:
		edge.append([list[0], list[1] - 1, list[2]])
	if list[1] + 1 <= args.width - 1:
		edge.append([list[0], list[1] + 1, list[2]])
	if list[2] - 1 >= 0:
		edge.append([list[0], list[1], list[2] - 1])
	if list[2] + 1 <= 1:
		edge.append([list[0], list[1], list[2] + 1])
	return edge


# 筛选可行边
def getfeasibleedges(list1, list2):
	list = []
	for i in list2:
		if B[pointnumber(list1), pointnumber(i)] == 1:
			list.append(i)
	return list


# 筛选可行点
def getfeasiblepoint(list1, list2):
	list = []
	for i in list2:
		if list1[pointnumber(i)] == 1:
			list.append(i)
	return list


# 主函数
if __name__ == "__main__":
	
	read()
	haha = 0
	Minlength = 1000000000000000
	while True:
		lines = copy.deepcopy(line_point)
		linesnumber = len(lines)
		# print(haha)
		haha = haha + 1
		key = 0
		
		point1 = copy.deepcopy(point)
		length = 0
		for i in range(linesnumber):
			
			number = random.randint(0, len(lines) - 1)
			line = lines.pop(number)
			
			number = line.pop(0)
			
			route1 = copy.deepcopy(line)
			route2 = []
			
			route = []
			
			linelength = len(line)
			for j in range(linelength):
				
				pointtemp = copy.deepcopy(point1)
				
				rand = random.randint(0, len(line) - 1)
				point_n = line.pop(rand)
				route_n = []
				if j == 0:
					route1 = copy.deepcopy(line)
				else:
					
					route1 = copy.deepcopy(route2)
				# print(line)
				
				step = 0
				while True:
					if step > args.max_search_length:
						key = 1
						break
					step += 1
					route_n.append(point_n)
					pointtemp[pointnumber(point_n)] = 0
					nearpoint = getnearpoint(point_n)
					feasiblepoint = getfeasibleedges(point_n, nearpoint)
					mindistance = getmindistance(point_n, route1)
					
					if mindistance[1] == 1:
						route2 = route2 + route_n
						length += len(route_n)
						break
					else:
						feasiblepoint = getfeasiblepoint(pointtemp, feasiblepoint)
						if len(feasiblepoint) == 0:
							upoint = route_n.pop()
							pointtemp[pointnumber(upoint)] = 0
							if len(route_n) == 0:
								key = 1
								break
							else:
								point_n = route_n.pop()
						else:
							targetpoint = mindistance[0]
							minnearpoint = getmindistance(targetpoint, feasiblepoint)[0]
							rand = random.randint(0, 100000000) / 100000000
							if rand < args.p:
								point_n = minnearpoint
							else:
								rand = random.randint(0, len(feasiblepoint) - 1)
								point_n = feasiblepoint[rand]
				if key == 1:
					break
			
			if key == 1:
				break
			for k in route2:
				point1[pointnumber(k)] = 0
		if key == 1:
			print(haha, "寻路失败", Minlength)
		else:
			if length <= Minlength:
				Minlength = length
			print(haha, "寻路成功", length, Minlength)
