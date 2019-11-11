# {{ cookiecutter.project_name }}

This is a sample template for {{ cookiecutter.project_name }} - Below is a brief explanation of what we have generated for you:

```bash
.
├── Makefile                    <-- Make to automate build
├── README.md                   <-- This instructions file
├── hello-world                 <-- Source code for a lambda function
│   ├── hello_world.go          <-- CFC function code
│   ├── main.go                 <-- CFC function code
│   ├── go.mod                  <-- go mod file
│   ├── go.sum                  <-- go mod file
│   └── Makefile.go             <-- Makefile
└── template.yaml
```

## Requirements

* BSAM CLI already configured with at least PowerUser permission
* [Docker installed](https://www.docker.com/community-edition)

## Setup process

### Installing dependencies

There are two ways you can install dependencies and build go executable file.

#### Use BSAM install command
You can run as follows:

```
bsam local install
```

This step will mount local folder to container, use go mod to download dependencies and build against Makefile automaticlly.

#### Use go mod yourself

In another way, you can compile go function for yourselfs, this requires you have go env locally.

```bash
cd hello_world
go mod tidy
GOOS=linux GOARCH=amd64 go build -o hello_world
cd ../
```

We recommand that you use the BSAM CLI to do download dependencies and compile, it's more convenient.

**NOTE**: If you're not building the function on a Linux machine, you will need to specify the `GOOS` and `GOARCH` environment variables, this allows Golang to build your function for another system architecture and ensure compatability.

**BSAM CLI** is used to emulate CFC locally and uses our `template.yaml` to understand how to bootstrap this environment (runtime, where the source code is, etc.)

## Packaging and deployment

BCE CFC Golang runtime requires a executable binary file. BSAM will use `CodeUri` property to know where to look up for the binary:

```yaml
...
    HelloWorldFunction:
        Type: BCE::Serverless::Function
        Properties:
            CodeUri: hello_world/
            ...
```

Next, run the following command to package function to a local zip file:

```bash
bsam package
```

Next, the following command will use CFC api to create or update function.

```bash
bsam deploy
```

> **See [How to use BSAM CLI](https://cloud.baidu.com/doc/CFC/s/6jzmfw35p) for more details in how to get started.**