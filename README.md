# ModflowDataCollector

## 项目简介

ModflowDataCollector是一个用于创建、配置和运行MODFLOW 6地下水流动与污染模型的工具库。该项目提供了简洁的API，用于定义模型场景、设置参数和执行模拟，帮助研究人员和工程师更高效地进行地下水污染模拟分析。

## 功能特点

- 场景配置：通过简洁的API设置模型参数、时间步长、空间离散化等
- 模型构建：自动生成MODFLOW 6输入文件
- 模拟执行：运行MODFLOW 6模拟并获取结果
- 支持流动模型和污染物运移模型
- 场景参数持久化：将配置保存为JSON文件，便于重复使用和版本控制

## 项目结构

```
ModflowDataCollector/
├── src/
│   ├── model/
│   │   └── model_builder.py    # MODFLOW 6模型构建器
│   ├── scenario/
│   │   ├── __init__.py
│   │   ├── scenario_loader.py  # 场景加载器
│   │   └── scenario_writer.py  # 场景写入器
│   ├── __init__.py
│   └── normal_2d_sim.py
├── test/
│   ├── __init__.py
│   └── scenariotest.py         # 测试脚本
├── .gitignore
├── main.py                     # 主入口
└── README.md
```

## 安装

1. 克隆项目到本地

```bash
git clone https://github.com/yourusername/ModflowDataCollector.git
cd ModflowDataCollector
```

2. 安装依赖

项目依赖于MODFLOW 6和相关Python库。请确保已安装：

- Python 3.6+
- MODFLOW 6
- NumPy

## 快速开始

### 基本使用流程

1. 创建场景写入器
2. 配置模型参数
3. 写入场景配置
4. 加载场景
5. 构建模型
6. 运行模拟

### 示例代码

```python
from src.scenario.scenario_writer import ScenarioWriter
from src.scenario.scenario_loader import ScenarioLoader
from src.model.model_builder import Modflow6Builder

# 创建场景写入器
sw = ScenarioWriter("test_scenario")

# 设置时间参数
sw.set_time(12, 30, 30, 1)

# 设置空间离散化
sw.set_discretization(1, 10, 10, 10, 10, 10, 100, -5)

# 设置渗透系数
sw.set_k(0.3)

# 设置初始水头
sw.set_initial_head(0.0)

# 设置恒定水头边界
sw.set_constant_head([(0,5,5), (0,4,6)])

# 设置抽水井
sw.set_well([[(0,2,3), 10, 10]])

# 设置初始浓度
sw.set_initial_concentration(0.1)

# 设置浓度边界
sw.set_cncspd([(0,5,5), (0,4,6)])

# 设置流动模型求解器参数
nouter, ninner = 100, 300
hclose, rclose, relax = 1e-6, 1e-6, 1.0
sw.set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)

# 写入场景配置
sw.write()

# 加载场景
sl = ScenarioLoader("test_scenario")

# 构建模型
mb = Modflow6Builder(sl)
sim = mb.build()

# 运行模拟
sim.run_simulation(silent=False, report=True)
```

## 核心组件

### ScenarioWriter

用于创建和配置模型场景的类，提供以下主要方法：

- `set_time(nper, perlen, nstp, tsmult, unit="days")`: 设置时间参数
- `set_discretization(nlay, nrow, ncol, delr, delc, delz, top, botm)`: 设置空间离散化
- `set_k(k11, k33=None)`: 设置渗透系数
- `set_initial_head(initial_head)`: 设置初始水头
- `set_constant_head(chdspd_posi, target_period=0)`: 设置恒定水头边界
- `set_well(spd, target_period=0)`: 设置抽水井
- `set_initial_concentration(initial_concentration)`: 设置初始浓度
- `set_cncspd(cncspd_posi, target_period=0)`: 设置浓度边界
- `set_flowmodel_solver(hclose, nouter, ninner, rclose, relax)`: 设置流动模型求解器参数
- `write()`: 写入场景配置到JSON文件

### ScenarioLoader

用于加载场景配置的类，从JSON文件中读取模型参数。

### Modflow6Builder

用于构建MODFLOW 6模型的类，根据加载的场景配置生成输入文件并构建模型。

## 运行测试

```bash
python main.py
```

这将运行`test/scenariotest.py`中的测试脚本，创建一个测试场景并运行模拟。

## 依赖项

- Python 3.6+
- NumPy
- MODFLOW 6

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请联系项目维护者。
