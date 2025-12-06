# RMYC Raspi Framework

**RMYC Raspi Framework** 是一个使用 *Raspberry Pi* 控制 *RM-S1/EP机器人*的 *Python* 框架。

## 学习

移步 [RMYC Raspi Framework Wiki](https://github.com/n1ghts4kura/rmyc-raspi-framework/wiki)

## 快速开始

### 快速接入比赛

#### 1. 安装虚拟环境

```bash
$ python -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 200 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

#### 2. 提升CPU性能（可选）

```bash
$ sudo sh ./tools/set_cpu_performance.sh
$ sudo sh ./verify_power.sh # 检验效果
```

```bash
# 安装 CPU 性能提升开机自启 服务 (可选)
$ sudo sh ./tools/install_cpu_performance_service.sh
# 卸载 CPU 性能提升开机自启 服务 (可选)
$ sudo sh ./tools/uninstall_cpu_performance_service.sh
```

#### 3. 运行 比赛流程

```bash
$ python -m src.main
```

### 数据采集工具

```bash
$ python -m src.backend.app
```

访问 [http://<树莓派IP地址>:5000/collector]("") （请根据实际情况修改地址）


## 致谢

- 2027届 **Aunnno** *自瞄模型相关* [*仓库地址*](https://github.com/Aunnno/RMYC-recognition)

- **2026 & 2027 届全体成员**

> **=v=**
