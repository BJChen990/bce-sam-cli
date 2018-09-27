# {{ cookiecutter.project_name }}

This is a sample template for {{ cookiecutter.project_name }} - Below is a brief explanation of what we have generated for you:

```bash
.
├── README.md                   <-- This instructions file
├── hello_world                 <-- Source code for a CFC function
│   ├── __init__.py
│   └── app.py                  <-- CFC function code
├── requirements.txt            <-- Python dependencies
├── template.yaml               <-- BSAM template
└── tests                       <-- Unit tests
    └── unit
        ├── __init__.py
        └── test_handler.py
```

## Requirements

* BCE CLI already configured with at least PowerUser permission
{%- if cookiecutter.runtime == 'python3.6' %}
* [Python 3 installed](https://www.python.org/downloads/)
{%- else %}
* [Python 2.7 installed](https://www.python.org/downloads/)
{%- endif %}
* [Docker installed](https://www.docker.com/community-edition)
* [Python Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

## Setup process

### Installing dependencies

BCE CFC requires a flat folder with the application as well as its dependencies. Therefore, we need to have a 2 step process in order to enable local testing as well as packaging/deployment later on - This consist of two commands you can run as follows:

```bash
pip install -r requirements.txt -t hello_world/build/
cp hello_world/*.py hello_world/build/
```

1. Step 1 install our dependencies into ``build`` folder 
2. Step 2 copies our application into ``build`` folder

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

We use **Pytest** for testing our code and you can install it using pip: ``pip install pytest`` 

Next, we run `pytest` against our `tests` folder to run our initial unit tests:

```bash
python -m pytest tests/ -v
```

**NOTE**: It is recommended to use a Python Virtual environment to separate your application development from  your system Python installation.

# Appendix

### Python Virtual environment

{%- if cookiecutter.runtime == 'python3.6' %}
**In case you're new to this**, python3 comes with `virtualenv` library by default so you can simply run the following:

1. Create a new virtual environment
2. Install dependencies in the new virtual environment

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
{%- else %}
**In case you're new to this**, python2 `virtualenv` module is not available in the standard library so we need to install it and then we can install our dependencies:

1. Create a new virtual environment
2. Install dependencies in the new virtual environment

```bash
pip install virtualenv
virtualenv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
{%- endif %}


**NOTE:** You can find more information about Virtual Environment at [Python Official Docs here](https://docs.python.org/3/tutorial/venv.html). Alternatively, you may want to look at [Pipenv](https://github.com/pypa/pipenv) as the new way of setting up development workflows
