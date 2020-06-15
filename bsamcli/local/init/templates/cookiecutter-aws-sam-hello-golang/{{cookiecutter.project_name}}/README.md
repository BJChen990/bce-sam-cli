# {{ cookiecutter.project_name }}

本项目是 {{ cookiecutter.project_name }} 的示例模板，项目结构如下：

```bash
.
├── README.md
├── src                         <-- 源文件文件夹，存放函数源码和依赖库
│   ├── index.go                <-- golang 函数源码
│   ├── main.go                 <-- golang 函数源码
│   ├── go.mod                  <-- go mod 依赖管理
│   ├── go.sum                  <-- go mod 依赖管理
│   └── Makefile                <-- 执行 make 自动编译
└── template.yaml
```

## 使用前提

* BSAM CLI 已成功安装
* [Docker 已成功安装](https://www.docker.com/community-edition)

## 函数依赖安装

CFC 执行 Golang 函数需要将函数提前编译成可执行文件。对 Golang 函数来说，您有两种编译方式。

### 手动下载依赖并编译

以本模板项目为例，您可执行如下命令：

```bash
cd src
go mod tidy
GOOS=linux GOARCH=amd64 go build -o index
cd ..
```

### 使用 BSAM 命令
若您的环境缺少相关工具，您可使用 BSAM 内置的功能安装依赖，执行如下命令:

```
bsam local install
```

BSAM 会把项目路径挂载到 Docker 容器中，并在容器中自动下载依赖并执行 make。

**NOTE**: 如果您不是在 Linux 环境中编译函数，您必须指定 `GOOS` 和 `GOARCH` 环境变量，以保证编译结果能在 CFC 的环境中运行。

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

若您在 windows 系统中使用 bsam，请尽量使用 bootstrap 文件，在其中自定义如何执行您的函数，比如

```
#!/bin/bash

ExecStart=(
    ./index
)
```

## 函数打包与部署

BSAM 根据 `CodeUri` 参数获取要部署的文件的路径。

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