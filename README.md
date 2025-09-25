# RMYC Raspi Framework

**RMYC Raspi Framework** 是一个使用 *Raspberry Pi* 控制 *RM-S1/EP机器人*的 *Python* 框架

## Thanks 2:

- 感谢 **Aunnno** 编写的 *图像识别方案*

    > 图像识别训练&使用 项目地址 [***click me***](https://github.com/Aunnno/RMYC-recognition)

## Usage:

1. 安装虚拟环境
```bash
$ python -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 200 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

2. 使用

- 测试检测结果

```bash
$ python src/test_annotation.py
```

- 正常运行

```bash
$ python src/main.py
```
