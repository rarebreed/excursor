# excursor

excursor means to scout or spy in latin.  excursor is a tool to learn python, mojo, and machine learning. It does so by
building up some projects and notebooks to introduce concepts

## Prerequisites

excursor uses poetry for project management, so you will need to have poetry installed.  It is also highly recommended
to install a virtual environment in 

- install python devel dependencies
- install asdf
- Install pipx
- Install virtualenv
- Create a virtualenv
- Install poetry

### Install python development deps

You can follow the directions here

If you're on a mac, basically do this

```
brew install openssl readline sqlite3 xz zlib tcl-tk
```

### Install asdf and the python plugin

First, install asdf itself

```
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.12.0
```

If you are using zsh, add the following to your `~/.zshrc` file

```
. "$HOME/.asdf/asdf.sh"
```

Then, either restart your shell, or source the zshrc file

```
source ~/.zshrc
```

Then, add the python plugin for asdf, install a python version, and make it your global python

```
asdf plugin add python https://github.com/danhper/asdf-python.git
asdf install python 3.11.5
asdf global python 3.11.5
asdf current
```

### Install pipx

Where `pip` is meant to install python _libraries_ as dependencies for a project, `pipx` is for installing _executables_
that your system may need.  To install pipx itself:

```
pip install pipx
pipx ensurepath
```
You may want to restart your shell, or source the `zshrc` file again, so that the path that pipx installs to is in your
system's PATH.

### Install a virtual env

We will use virtualenv for our virtual environment management.  `pyenv` can setup both a python version and virtualenvs
for you, but with asdf, it's a one stop shop (you can install Java, Node, maven, gradle, etc all with asdf)

```
pipx install virtualenv
virtualenv -p python3.11.5 /path/to/excursor/.venv
```

### Install poetry

You can use their shell script to install poetry

```
curl -sSL https://install.python-poetry.org | python3 -
```

To test that it works:

```
poetry -V
```

You can also look at the [directions from poetry](https://python-poetry.org/docs/)

## Install python dependencies for excursor

Now that you finally have all the prereqs out of the way, you can install the deps for excursor itself

```
git clone https://github.com/rarebreed/excursor.git
cd excursor
poetry install --all-extras --with dev
```

This may take a minute or two for poetry to calculate all the dependencies and download them.
