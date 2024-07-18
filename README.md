# Ditto
一个图区块链系统的模拟仿真框架，通过交互式可视化界面展示区块图生成过程、共识算法执行结果，模拟多种网络攻击。项目取名为宝可梦动漫里的百变怪，意为具备变身技能，可模仿任意图区块链系统。

## 项目目标
以开源项目[Phantom](https://github.com/AvivYaish/PHANTOM.git)为基础，扩展其模拟框架的功能和内容：
1. 能模拟分散型（朴素）、平行型、收敛型（主链）三种类型的图区块链。
2. 能配置矿工行为，将收敛型图区块链退化成最长链模式，以模拟单链结构的区块链。
3. 能模拟多种网络攻击，包括自私挖矿攻击（selfish mining attack）、日蚀攻击（eclipse attack）。
4. 能设定区块包含的特殊交易，如重复交易（repeated transaction）、冲突交易（conflicted transaction）。
5. 能控制区块生成速率，且按高度或深度组织区块，友好地交互式可视化。

## 项目依赖
项目采用 python>=3.10 编程语言，依赖如下重要的库。
- networkx  # 复杂网络分析库
- numpy  # 用于计算泊松分布的数学库
- simpy  # 基于过程的离散事件仿真框架
- bokeh  # 面向浏览器的交互式可视化库
- pytest  # python测试框架
- ...

## 项目使用
- 测试

安装测试所需的依赖包，执行项目批量测试。
```commandline
cd Ditto
pip install .[test]
python -m pytest
```

- 运行 

安装运行所需的依赖包，执行项目入口方法。
```commandline
cd Ditto
pip install .
python -m ditto.main
```
