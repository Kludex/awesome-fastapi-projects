# Awesome FastAPI Projects

View the website: https://kludex.github.io/awesome-fastapi-projects/

## Local Development

### Setup

#### Python and Virtual Environment

The instructions below assume you have [pyenv](https://github.com/pyenv/pyenv) installed.
If you don't, use any other method to create a virtual environment
and install Python 3.11.4.

- Install Python 3.11.4

```shell
pyenv install 3.11.4
```

- Create a virtual environment

```shell
pyenv virtualenv 3.11.4 awesome-fastapi-projects
```

- Activate the virtual environment

```shell
pyenv local awesome-fastapi-projects
```

#### Install dependencies and pre-commit hooks

There is a `Makefile` with some useful commands to help you get started.
For available commands, run `make help`. To install dependencies and pre-commit hooks, run:

```shell
make
```

#### Frontend

The frontend is built with [React](https://reactjs.org/) and [Next.js](https://nextjs.org/).
It is being statically built and served on GitHub Pages: https://kludex.github.io/awesome-fastapi-projects/

To run the frontend locally, you need to install [Node.js](https://nodejs.org/en/) and [pnpm](https://pnpm.io/).
The node version is specified in the `.node-version` file.
To easily manage the node version, you can use [fnm](https://github.com/Schniz/fnm).
Then, run the following commands:

```shell
make front
```

This will install the dependencies and start the development server.
The frontend will be available at http://localhost:3000.
