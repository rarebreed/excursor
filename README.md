# excursor

excursor means to scout or spy in latin.  excursor is a tool to learn python, mojo, and machine learning. It does so by
building up some projects and notebooks to introduce concepts

## Installing Prerequisites

excursor comes with an installer module to install the development tools that will be needed.  You will need at a 
minimum the following installed:

- git
- python 3.9+
- pip

First, create a virtual environment

```bash
git clone https://github.com/rarebreed/excursor.git
cd excursor
python -m venv setup
source setup/bin/activate
pip install daak
```

This will clone excursor on your system, create a virtual environment, activate it, and install a module dependency.
Now you can run the following commands:

- Install python devel deps: `python -m excursor.core.installer sys`
- Install asdf python manager: `python -m excursor.core.installer asdf`
- Install poetry project manager: `python -m excursor.core.installer poetry`
- Install virtualenv: `python -m excursor.core.installer venv`

The `venv` command at the end will also install a new virtual environment in excursor.  You can `rm -rf` the `setup`
directory from earlier and

```bash
source venv/bin/activate
```

This will activate the new virtual environment.  Then you can install the full excursor dependencies

```bash
poetry install --all-extras --with dev
```

Skip any of the commands above if you already have asdf, poetry, or virtualenv already installed.