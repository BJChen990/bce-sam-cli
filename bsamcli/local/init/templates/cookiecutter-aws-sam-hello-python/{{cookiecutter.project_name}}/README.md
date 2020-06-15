# {{ cookiecutter.project_name }}

本项目是 {{ cookiecutter.project_name }} 的示例模板，项目结构如下：

```bash
.
├── README.md
├── src                         <-- 源文件文件夹，存放函数源码和依赖库
│   ├── __init__.py
│   ├── index.py                <-- python 函数源码
│   └── requirements.txt        <-- Python 依赖管理文件
├── template.yaml               <-- BSAM 模型文件
└── tests                       <-- 单元测试
    └── unit
        ├── __init__.py
        └── test_handler.py
```

## 使用前提

* BSAM CLI 已成功安装
* [Docker 已成功安装](https://www.docker.com/community-edition)

## 函数依赖安装

CFC 执行函数不仅需要函数源码，也需要函数的依赖库。因此，在执行函数前，您需要先安装函数依赖库。对 Python 函数来说，您有两种安装方式。

### Use pip

您可以使用 pip 或其它工具自行安装依赖库，或者把您个人的 python 库放到代码所在目录中，比如：

```bash
pip install -r src/requirements.txt -t src/
```

### 使用 BSAM 命令
若您的环境缺少相关工具，您可使用 BSAM 内置的功能安装依赖，执行如下命令:

```
bsam local install
```

BSAM 会把项目路径挂载到 Docker 容器中，并在容器中使用 pip 自动安装依赖库到函数代码所在目录。

## 生成触发器 event

若您的函数会被触发器调用，您可以给函数传入该触发器的事件，以验证函数对 event 的处理。执行如下命令获取某个特定事件的 event:

```
bsam local generate-event dueros intent-answer
```

更多 event 可执行如下命令查看：

```
bsam local generate-event -h
```

## 函数执行

BSAM CLI 使用 `template.yaml` 获取函数的运行时、源码文件路径等信息，从而得知如何执行函数。您可以使用以下方式执行函数:

```
# 输出 json 字符串作为 event 重定向给函数
echo '{"foo": "bar"}' | bsam local invoke HelloWorldFunction

# 把 json 文件内容作为 event 重定向给函数，并跳过检查远程镜像更新和拉取
cat event.json | bsam local invoke --skip-pull-image HelloWorldFunction

# 不传 event 给函数
bsam local invoke HelloWorldFunction --no-event --skip-pull-image
```

## 函数打包与部署

CFC Python 函数执行时需要相关的依赖库文件，所以您需要将依赖库文件与函数源文件一起打包部署。BSAM 根据 `CodeUri` 参数获取这些文件所在路径。

```yaml
...
    HelloWorldFunction:
        Type: BCE::Serverless::Function
        Properties:
            CodeUri: src/
            ...
```

执行如下命令会把 `CodeUri` 目录下的文件打成 zip 包：

```bash
bsam package
```

接下来，您可以使用 `deploy` 命令把函数创建或更新到云端。

```bash
bsam deploy
```

> **关于 BSAM CLI 的更多用法，请查看该文档 https://cloud.baidu.com/doc/CFC/s/6jzmfw35p**