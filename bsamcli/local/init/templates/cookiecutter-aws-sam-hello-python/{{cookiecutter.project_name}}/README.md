# {{ cookiecutter.project_name }}

This is a sample template for {{ cookiecutter.project_name }} - Below is a brief explanation of what we have generated for you:

```bash
.
├── README.md                   <-- This instructions file
├── hello_world                 <-- Source code for a CFC function
│   ├── __init__.py
│   ├── index.py                <-- CFC function code
│   └── requirements.txt        <-- Python dependencies
├── template.yaml               <-- BSAM template
└── tests                       <-- Unit tests
    └── unit
        ├── __init__.py
        └── test_handler.py
```

## Requirements

* BCE CLI already configured with at least PowerUser permission
* [Docker installed](https://www.docker.com/community-edition)

## Setup process

### Installing dependencies

BCE CFC requires a flat folder with the application as well as its dependencies. Therefore, we need to have a process in order to enable local testing as well as packaging/deployment later on. There are two ways you can install dependencies.

#### Use BSAM install command
You can run as follows:

```
bsam local install
```

This step will mount local folder to container, and install our dependencies into the function code folder automaticlly.


#### Use pip

You can use pip or other tools to manage dependencies, you can also put your personal library in the folder.

```bash
pip install -r hello_world/requirements.txt -t hello_world/
```

We recommand that you use the BSAM CLI to do install denepdencies.

**NOTE:** As you change your application code as well as dependencies during development you'll need to make sure these steps are repeated in order to execute your CFC.

**BSAM CLI** is used to emulate CFC locally and uses our `template.yaml` to understand how to bootstrap this environment (runtime, where the source code is, etc.)

## Packaging and deployment

BCE CFC Python runtime requires a flat folder with all dependencies including the application. BSAM will use `CodeUri` property to know where to look up for both application and dependencies:

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

## Testing

### Requirements
{%- if cookiecutter.runtime == 'python3.6' %}
* [Python 3 installed](https://www.python.org/downloads/)
{%- else %}
* [Python 2.7 installed](https://www.python.org/downloads/)
{%- endif %}
* [Pytest installed](https://docs.pytest.org/en/latest/getting-started.html)

We use **Pytest** for testing our code and you can install it using pip: ``pip install pytest`` 

Next, we run `pytest` against our `tests` folder to run our initial unit tests:

```bash
python -m pytest tests/ -v
```

> **See [How to use BSAM CLI](https://cloud.baidu.com/doc/CFC/QuickGuide.html#BSAM.20CLI.E4.BD.BF.E7.94.A8.E7.A4.BA.E4.BE.8B) for more details in how to get started.**