# nectarine

Library to load configuration from various sources.

## Requirements

Nectarine requires Python 3.6 or above, and has been tested using Python 3.8.

## Installing

Nectarine can be installed through pip.

```
$ pip3 install nectarine        # Install the basic version
$ pip3 install nectarine[yaml]  # Install the YAML extension
```

## Providers

Nectarine loads the configuration from different back-ends called **providers**. The table below lists the available
providers.

| Name       | Description                                                  |
| ---------- | ------------------------------------------------------------ |
| arguments  | A provider that reads from the program arguments             |
| env        | A provider that reads from the program environment variables |
| dictionary | A provider that reads from a user-provided dictionary        |
| json       | A provider that reads from a user-provided JSON file         |
| yaml       | A provider that reads from a user-provided YAML file         |

## Step-by-step example

Nectarine gives you the ability to describe a configuration using Python's dataclasses, and load it from various
sources (program arguments, configuration files, ...).

Let's consider a program that consumes events from a RabbitMQ broker (for example, using the awesome `pika` library!).
That little program should of course allow the user to configure connection parameters such as the broker's host and
listening port, the credentials to use, etc.

Our program will accept configuration from 3 different providers:
- the program arguments
- the program environment
- a JSON configuration file, say `./conf.json` with fields for the host / port / username / password

The idea here is to allow the user to quickly override the configuration file by using the environment or the arguments.

In order to represent those connection parameters, we create the following dataclass:

```python
from dataclasses import dataclass

@dataclass
class RabbitMQ:
    host: str
    username: str
    password: str
    port: int = 5671
```

The next step is to communicate with the user, obtain the configuration, and create an instance of `RabbitMQ`
with it. Let's see how we can achieve that with Nectarine.

Nectarine provides a `load` function, which needs two things: the type to load, and a list of providers to load from.

We already have our target type (which is `RabbitMQ`), thus we need to select our providers:
- for program arguments, the `arguments` provider
- for program environment, the `env` provider
- for the JSON file, the `json` provider

Now, we can call the `load` function like below and retrieve its result:

```python
from nectarine import load, arguments, env, json

rabbitmq = load(
    target=RabbitMQ,
    providers=[
        arguments(),
        env(prefix="RABBITMQ_"),
        json("./conf.json")
    ]
)
print(rabbitmq)
```

That's pretty much it! The `rabbitmq` variable is now loaded with our configuration when we run the program:
```
$ echo '{"host": "localhost", "port": 5671, "username": "user", "password": "pass"}' > ./conf.json
$ ./consumer.py
RabbitMQ(host='localhost', username='user', password='pass', port=5671)
$ ./consumer.py --port 1234
RabbitMQ(host='localhost', username='user', password='pass', port=1234)
```

## Features

- [x] Multiple configuration providers: program arguments, environment, configuration files, ...
- [x] Value overriding: higher-priority providers override values from lower-priority providers
- [x] Complex structures: nested dataclasses and collections are supported
- [x] Type checking: configuration data is checked against the type hints provided in your dataclasses
- [x] Dataclasses features: default values or factories can be specified just as in regular dataclasses
