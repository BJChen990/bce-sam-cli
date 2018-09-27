# {{ cookiecutter.project_name }}

This is a sample template for {{ cookiecutter.project_name }} - Below is a brief explanation of what we have generated for you:

```bash
.
├── README.md                   <-- This instructions file
├── hello_world                 <-- Source code for a cfc function
│   ├── app.js                  <-- CFC function code
│   ├── package.json            <-- NodeJS dependencies
│   └── tests                   <-- Unit tests
│       └── unit
│           └── test_handler.js
└── template.yaml               <-- BCE SAM template
```

## Requirements

* BCE CLI already configured with at least PowerUser permission
{%- if cookiecutter.runtime == 'nodejs6.10' %}
* [NodeJS 6.10 installed](https://nodejs.org/en/download/releases/)
{%- elif cookiecutter.runtime =='nodejs4.3' %}
* [NodeJS 4.3 installed](https://nodejs.org/en/download/releases/)
{%- else %}
* [NodeJS 8.10+ installed](https://nodejs.org/en/download/)
{%- endif %}
* [Docker installed](https://www.docker.com/community-edition)

## Setup process

### Installing dependencies

In this example we use `npm` but you can use `yarn` if you prefer to manage NodeJS dependencies:

```bash
cd hello_world
npm install
cd ../
```

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

We use `mocha` for testing our code and it is already added in `package.json` under `scripts`, so that we can simply run the following command to run our tests:

```bash
cd hello_world
npm run test
```
