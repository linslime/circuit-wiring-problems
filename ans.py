import pandas as pd
import copy
import random

#常量
sheet_name = '实例1'
m = 16
n = 16
M = 10000
p = 0.975

#全局变量
B = {}
margin = []
radius = []

line_point = []

point = [1 for i in range(2 * m * n)]
pointtemp = []

#读数据
def readread():
    df1 = pd.read_excel(r'D:\Desktop\model7\one.xlsx', sheet_name=sheet_name)
    df2 = pd.read_excel(r'D:\Desktop\model7\two.xlsx', sheet_name=sheet_name)
    df3 = pd.read_excel(r'D:\Desktop\model7\three.xlsx', sheet_name=sheet_name)
    df4 = pd.read_excel(r'D:\Desktop\model7\four.xlsx', sheet_name=sheet_name)

    data1 = df1.values.tolist()
    data2 = df2.values.tolist()
    data3 = df3.values.tolist()
    data4 = df4.values.tolist()

    for i in data1:
        one = pointnumber(i[:3])
        two = pointnumber(i[3:])
        B[one,two] = 1
        B[two,one] = 1

    for i in data2:
        one = pointnumber(i[:3])
        two = pointnumber(i[3:])
        B[one,two] = 1
        B[two,one] = 1

    linetemp = []
    for i in range(int(len(data3[1])/2)):
        linetemp.append((data3[1][i]))
    margin = data3[0][0::2]
    radius = data3[0][1::2]
    for i in range(len(margin)):
        margin[i] = int(margin[i])
        radius[i] = int(radius[i])
        linetemp[i] = int(linetemp[i])

    for i in data4:
        # print(i)
        point[pointnumber(i)] = 0

    for i in range(len(linetemp)):
        list = [i] + data4[:linetemp[i]]
        data4 = data4[linetemp[i]:]
        line_point.append(list)

#点号
def pointnumber(list):
    return list[0] + list[1] * m + list[2] * m * n

#曼哈顿距离
def Manhattandistance(list1,list2):
    return sum([abs(list1[i] - list2[i]) for i in range(3)])

#求出最小距离目标
def getmindistance(list1,list2):
    mindistance = 100000000000000
    mindistancepoint = []
    for i in range(len(list2)):
        distance = Manhattandistance(list1,list2[i])
        if distance < mindistance:
            mindistancepoint = list2[i]
            mindistance = distance
    return [mindistancepoint,mindistance]

#寻找临近点
def getnearpoint(list):
    edge = []
    if list[0] - 1 >= 0:
        edge.append([list[0] - 1,list[1],list[2]])
    if list[0] + 1 <= m - 1:
        edge.append([list[0] + 1,list[1],list[2]])
    if list[1] - 1 >= 0:
        edge.append([list[0],list[1] - 1,list[2]])
    if list[1] + 1 <= n - 1:
        edge.append([list[0],list[1] + 1,list[2]])
    if list[2] - 1 >= 0:
        edge.append([list[0],list[1],list[2] - 1])
    if list[2] + 1 <= 1:
        edge.append([list[0],list[1],list[2] + 1])
    return edge

#筛选可行边
def getfeasibleedges(list1,list2):
    list = []
    for i in list2:
        if B[pointnumber(list1) , pointnumber(i)] == 1:
            list.append(i)
    return list

#筛选可行点
def getfeasiblepoint(list1,list2):
    list = []
    for i in list2:
        if list1[pointnumber(i)] == 1:
            list.append(i)
    return list

#主函数
if __name__ == "__main__":

    readread()
    haha = 0
    Minlength = 1000000000000000
    Minlengthpoint = []
    while True:
        lines = copy.deepcopy(line_point)
        linesnumber = len(lines)
        # print(haha)
        haha = haha + 1
        key = 0

        point1 = copy.deepcopy(point)
        length = 0
        route = []
        for i in range(linesnumber):

            number = random.randint(0,len(lines) - 1)
            line = lines.pop(number)

            number = line.pop(0)

            route1 = copy.deepcopy(line)
            route2 = []

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

                #print(line)
                step = 0
                while True:
                    if step > M:
                        key = 1
                        break
                    step += 1
                    route_n.append(point_n )
                    pointtemp[pointnumber(point_n)] = 0
                    nearpoint = getnearpoint(point_n)
                    feasiblepoint = getfeasibleedges(point_n,nearpoint)
                    mindistance = getmindistance(point_n,route1)

                    if mindistance[1] == 1:
                        route2 = route2 + route_n
                        length += len(route_n)
                        break
                    else:
                        feasiblepoint = getfeasiblepoint(pointtemp,feasiblepoint)
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
                            minnearpoint = getmindistance(targetpoint,feasiblepoint)[0]
                            rand = random.randint(0, 100000000) / 100000000
                            if rand < p:
                                point_n = minnearpoint
                            else:
                                rand = random.randint(0, len(feasiblepoint) - 1)
                                point_n = feasiblepoint[rand]
                if key == 1:
                    break

            route .append(route2)
            if key == 1:
                break
            for k in route2:
                point1[pointnumber(k)] = 0

        if key == 1:
            print(haha,"寻路失败",Minlength)
        else:
            if length <= Minlength:
                Minlength = length
                Minlengthpoint = copy.deepcopy(route)
                f = open("D:\Desktop\\test.txt", "w")
                f.write(str(Minlengthpoint))

            print(haha,"寻路成功",length,Minlength,len(Minlengthpoint))

