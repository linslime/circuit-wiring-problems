# 求解 Steiner Forest Problem
## 方法一  
____  
__使用A*算法依次生成每一个斯坦纳树，如果发现无法成功则全部重新开始布线，再通过蒙德卡洛法优化。__

针对不同的数据有如下命令方法  
* 使用数据集instance1，全连接
```bash
python RawMethod.py --length=16 --width=16 --p=0.975 --max_search_length=2000 --data_path="./data/instance1" --is_connected="connected"
```

* 使用数据集instance1,非全连接
```bash
python RawMethod.py --length=16 --width=16 --p=0.975 --max_search_length=2000 --data_path="./data/instance1" --is_connected="unconnected"
```

* 使用数据集instance2,全连接
```bash
python RawMethod.py --length=64 --width=64 --p=0.9 --max_search_length=50000 --data_path="./data/instance2" --is_connected="connected"
```

* 使用数据集instance2,非全连接
```bash
python RawMethod.py --length=64 --width=64 --p=0.9 --max_search_length=50000 --data_path="./data/instance2" --is_connected="unconnected"
```

* 使用数据集instance3,全连接
```bash
python RawMethod.py --length=128 --width=128 --p=0.9 --max_search_length=80000 --data_path="./data/instance3" --is_connected="connected"
```

*使用数据集instance3,非全连接
```bash
python RawMethod.py --length=128 --width=128 --p=0.9 --max_search_length=80000 --data_path="./data/instance3" --is_connected="unconnected"
```