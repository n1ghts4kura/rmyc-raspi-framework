# RMYC Raspi Framework

**RMYC Raspi Framework** 是一个使用 *Raspberry Pi* 控制 *RM-S1/EP机器人*的 *Python* 框架。

## Designing

### 上层设计

- **运动控制** 模块  
顾名思义控制机器人的运动，如前进后退，发射水弹。

- **技能** 模块  
管理技能，将注册的技能与对应的按键绑定。

### 下层设计

- **串口通信** 模块  
接收/发送数据 给机器人。

---

## Usage

### 安装虚拟环境

```bash
$ python -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 200 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

### 使用

#### 比赛流程

```bash
$ python src/main.py
```

#### 串口交互

```bash
$ python src/repl.py
```

## Thanks to

- 2027届 **Aunnno** *自瞄模型相关* [**click me**](https://github.com/Aunnno/RMYC-recognition)

- 2026 & 2027 届全体成员

> **=v=**
