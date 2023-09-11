# excursor

excursor means to scout or spy in latin.  excursor is a tool to learn python, mojo, and machine learning. It does so by
building up some projects and notebooks to introduce concepts

## Prerequisites

excursor uses poetry for project management, so you will need to have poetry installed.  It is also highly recommended
to install a virtual environment in 

- clone excursor project
- install python devel dependencies
- install asdf
- Install pipx
- Install virtualenv
- Create a virtualenv
- Install poetry

### Clone the excursor project

We will use excursor for all the materials in this training

```
git clone https://github.com/rarebreed/excursor.git
cd excursor
```

### Install python development deps

If you're on a mac, basically do this

```
brew install openssl readline sqlite3 xz zlib tcl-tk
```

Otherwise, can [follow the directions here](https://github.com/pyenv/pyenv/wiki#suggested-build-environment) for your 
system

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

Now that you finally have all the prereqs out of the way, you can install the deps for excursor itself.  You may need
to edit the pyproject.toml file depending on whether you are running on linux or a mac.  If you are running on linux
look for the following lines in the `pyproject.toml` file

```toml
# If you are on linux, uncomment the torch line below
#torch = {version = "^2.0.1+cpu", optional = true, source = "pytorch"}
# If you are not on a mac, comment this line out
torch = {version = "^2.0.1", optional = true}
ray = {extras = ["rllib", "serve", "tune"], version = "^2.6.1"}
```

If you are on linux, uncomment the line indicated

```toml
torch = {version = "^2.0.1+cpu", optional = true, source = "pytorch"}
```

And comment out the other torch dependency

```toml
torch = {version = "^2.0.1", optional = true}
```

Next, look for and uncomment out the following section

```toml
[[tool.poetry.source]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
priority = "supplemental"
```

This is so that we will use the "vanilla" CPU only version of pytorch (which will have limited ability to vectorize
the tensors and will therefore be slow).  This is one of the reasons we will cover the mojo language later.

```
poetry install --all-extras --with dev
```

This may take a minute or two for poetry to calculate all the dependencies and download them.
