# {{ cookiecutter.project_name }}

本项目是 {{ cookiecutter.project_name }} 的示例模板，项目结构如下：

```bash
.
├── README.md
├── src
│   ├── InvokeEvent.cs      <-- event 定义文件
│   ├── Program.cs          <-- 程序 main 入口
│   ├── StreamHandler.cs    <-- 用户函数入口
│   └── bsam_csharp.csproj  
└── template.yaml           <-- BSAM 模型文件
```

## 使用前提

* BSAM CLI 已成功安装
* [Docker 已成功安装](https://www.docker.com/community-edition)

## 函数依赖安装

CFC 执行 csharp 函数需要将函数提前编译成可执行文件，您有两种编译方式。

#### 手动下载依赖并编译

以本模板项目为例，您可执行如下命令：

```bash
cd src
dotnet publish -c Release
cd ..
```

#### 使用 BSAM 命令

若您的环境缺少相关工具，您可使用 BSAM 内置的功能安装依赖，执行如下命令:

```
bsam local install
```

BSAM 会把项目路径挂载到 Docker 容器中，并在容器中自动安装依赖并编译。

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

由于 dotnet publish 时的路径是固定的，所以 `CodeUri` 中无需 publish 后的子路径，BSAM CLI 会进入 `CodeUri` 下的 `bin/Release/netcoreapp2.2/publish/` 路径，并打包函数。

```yaml
...
    HelloWorldFunction:
        Type: BCE::Serverless::Function
        Properties:
            CodeUri: src/
            Handler: bsam_csharp::BaiduBce.CFC.Demo.StreamHandlerDemo
            ...
```

执行如下命令会把 `CodeUri` 子目录 publish 路径下的文件打包成 zip 文件：

```bash
bsam package
```

接下来，您可以使用 `deploy` 命令把函数创建或更新到云端。

```bash
bsam deploy
```

> **关于 BSAM CLI 的更多用法，请查看该文档 https://cloud.baidu.com/doc/CFC/s/6jzmfw35p**
> **关于 CSharp 函数的更多说明，请查看该文档 https://cloud.baidu.com/doc/CFC/s/Hk06piw4u**