# {{ cookiecutter.project_name }}

本项目是 {{ cookiecutter.project_name }} 的示例模板，项目结构如下：

```bash
.
├── README.md
├── hello_world                 <-- 存放函数相关源文件的文件夹
│   └── index.ps1               <-- Powershell 函数源文件
└── template.yaml               <-- BSAM 模型文件
```

## 使用前提

* BSAM CLI 已成功安装
* [Docker 已成功安装](https://www.docker.com/community-edition)

## 函数执行

您可以使用以下方式执行函数:

```
# 输出 json 字符串作为 event 重定向给函数
echo '{"foo": "bar"}' | bsam local invoke HelloWorldFunction

# 把 json 文件内容作为 event 重定向给函数，并跳过检查远程镜像更新和拉取
cat intent-answer.json | bsam local invoke --skip-pull-image HelloWorldFunction

# 不传 event 给函数
bsam local invoke HelloWorldFunction --no-event --skip-pull-image
```

## 函数打包与部署

BSAM 根据 `CodeUri` 参数获取函数文件所在路径。

```yaml
...
    HelloWorldFunction:
        Type: BCE::Serverless::Function
        Properties:
            CodeUri: hello_world/
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