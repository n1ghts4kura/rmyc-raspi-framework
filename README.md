# RMYC Raspi Framework

**RMYC Raspi Framework** 是一个使用 *Raspberry Pi* 控制 *RM-S1/EP机器人*的 *Python* 框架。

## 编码前提醒

### AI辅助

如果可以，请**每次编辑代码前**，使用**大模型工具**对该项目目前的开发进度等信息（如正在开发自瞄/正在开发寻路系统）进行**总结**，并记录到documents文件夹中的**一个特定文件**。

在**每次编辑代码后+提交前**，使用**大模型工具**对你改动后的项目开发进度等信息再次进行总结，对文档进行更新。

> 比如你最近在研究/完善**自瞄**，  
> 那么你应该在documents/文件夹中保存 你**对自瞄这一部分的 添加/改进**，命名要**清晰明确**。(比如  `aimassistant_model_improvement.md` )  
> 如果说有**几乎一样主题**的说明文件*已经存在*，那么你可以修改这个文件。  
> 否则*强烈建议***重新撰写一个文档**，保证每个文档的**相对独立性**，不被干扰，*以优化大模型编码工具输出*。  
>
> 具体AI编码指南，上网找教程吧。编者也不敢自诩大神。  

### 编码风格 \*\*[重要]\*\*

> *强迫症驱使。T_T (n1ghts4kura 2025/10/1)*

#### 变量/函数命名 (推荐)

1. **排列顺序**:  
    \[**<动词 verb>** + **<名词 noun>** + **<...>**\] *  
    如 `open_serial()`。

2. **单词使用**：  
    使用**简单单词+多词叠加**的策略。如：  
    | 不推荐 | 推荐 |
    | --- | --- |
    | `...` | `...` |

> 写到这突然举不出来例子了。(捂脸)

#### 流程设计

搁置

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
