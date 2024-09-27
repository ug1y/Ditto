# Ditto

一个混合型区块图模拟框架，其中区块图是指基于有向无环图的区块链。该框架可以交互式地展示区块图的生成、共识协议的执行， 
以及拜占庭攻击效果。该项目被命名为`Ditto`，取自宝可梦动漫里的百变怪，寓意该框架可以模拟各种图区块链系统。


### 目标

受开源项目 [PHANTOM](https://github.com/AvivYaish/PHANTOM.git) 和 
[py-swirld](https://github.com/Lapin0t/py-swirld.git) 的启发，本项目扩展了区块图模拟框架，
包括如下功能：
1. 能模拟发散型、平行型、收敛型三种类型的图区块链
2. 能配置矿工行为，令收敛型区块图退化为中本聪共识的单链结构（即模拟比特币系统）
3. 能模拟针对区块图的多种拜占庭攻击，包括自私挖矿攻击（selfish attacks），日蚀攻击（eclipse attacks）
4. 能设定区块包含的特殊交易，如重复交易（repeated transactions），冲突交易（repeated transactions），当前版本留空
5. 能控制区块生成速率，按高度组织区块，友好地交互式可视化


### 依赖

该项目支持 `python>=3.10` 编程语言，并依赖于以下库：
- networkx==3.3.0  # 复杂网络分析库
- numpy==1.26.0  # 用于计算泊松分布的数学库
- simpy==4.1.0  # 基于过程的离散事件仿真框架库
- bokeh==3.5.0  # 面向浏览器的交互式可视化库
- click==8.1.7  # 命令行工具接口库


### 安装

克隆本项目并执行如下命令安装：
```shell
git clone https://github.com/ug1y/Ditto.git
cd Ditto
pip install .
```

如果要基于当前项目进行开发，请按照如下方式安装。
```shell
git clone https://github.com/ug1y/Ditto.git
cd Ditto
pip install -e .
```


### 使用


入口方法是 `ditto.main`, 选项 `--help` 获取更多详细信息, 选项 `--version` 获取版本信息。
```shell
python -m ditto.main --help
python -m ditto.main --version
```

本项目有三种运行模式，可使用`--help`查看参数说明。

1. 给定参数运行一次模拟：
```shell
python -m ditto.main simu -n [net_template] -c [cons_method] \
                          -s [scale] -r [rate] -i [interval] -d [delay] \
                          -u [until] 
```

2. 指定端口运行bokeh服务器：
```shell
python -m ditto.main serv -p [port]
```

3. 在模拟中运行拜占庭攻击模式：
```shell
python -m ditto.main attk -n [net_template] -c [cons_method] \
                          -s [scale] -r [rate] -i [interval] -d [delay] \
                          -u [until] -t [times] -p [power]
```