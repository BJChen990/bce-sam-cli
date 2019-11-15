# {{ cookiecutter.project_name }}

This is a sample template for {{ cookiecutter.project_name }} - Below is a brief explanation of what we have generated for you:

```bash
.
├── README.md                               <-- This instructions file
├── pom.xml                                 <-- Java dependencies
├── src
│   ├── main
│   │   └── java
│   │       └── helloworld                  <-- Source code for a CFC function
│   │           └── Index.java              <-- CFC function code
│   └── test                                <-- Unit tests
│       └── java
│           └── helloworld
│               └── IndexTest.java
└── template.yaml
```

## Requirements

* BCE SAM CLI already configured with at least PowerUser permission
* [Docker installed](https://www.docker.com/community-edition)

## Setup process

### Installing dependencies and compile

BCE CFC requires a flat folder with the application as well as its dependencies. Therefore, we need to have a process in order to enable local testing as well as packaging/deployment later on. There are two ways you can install dependencies.

#### Use BSAM install command
You can run as follows:

```
bsam local install
```

This step will mount local folder to container, use maven to download dependencies and compile application into a JAR file.


#### Use mvn

You can use maven or other tools to manage dependencies.

```bash
mvn package
```

In order to avoid environmental inconsistencies, we recommand that you use the BSAM CLI to install and compile.

**NOTE:** As you change your application code as well as dependencies during development you'll need to make sure these steps are repeated in order to execute your CFC.

**BSAM CLI** is used to emulate CFC locally and uses our `template.yaml` to understand how to bootstrap this environment (runtime, where the source code is, etc.)

## Packaging and deployment

BCE CFC Java runtime accepts a standalone JAR file. BSAM will use `CodeUri` property to know the JAR file's location:

```yaml
...
    HelloWorldFunction:
        Type: BCE::Serverless::Function
        Properties:
            CodeUri: target/
            Handler: com.baidu.demo.SimpleHandler
```

Run the following command to package our CFC function to a local zip file:

```bash
bsam package
```

Next, the following command will use CFC api to create or update function.

```bash
bsam deploy
```

> **See [How to use BSAM CLI](https://cloud.baidu.com/doc/CFC/s/6jzmfw35p) for more details in how to get started.**
> **See [Java函数开发指南](https://cloud.baidu.com/doc/CFC/BestPractise.html#Java.E5.87.BD.E6.95.B0.E5.BC.80.E5.8F.91.E6.8C.87.E5.8D.97) for more details about java function.**

## Testing
### Requirements
Testing is not yet integrated into BSAM CLI, so you need to configure the environment before testing.
* [Maven installed](https://maven.apache.org/download.cgi)
* [JDK installed](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)

We use `JUnit` for testing our code and you can simply run the following command to run our tests:

```bash
mvn test
```