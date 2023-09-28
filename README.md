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
```

This will clone excursor on your system.  Then run the following commands:

- Install python devel deps: `python3 -m excursor.core.installer sys`
- Install asdf python manager: `python3 -m excursor.core.installer asdf`
- Activate asdf: `source ~/.zshrc`
- Install poetry project manager: `python3 -m excursor.core.installer poetry`
- Install virtualenv: `python3 -m excursor.core.installer venv`
- Optional (if you want python 3.9.x): `asdf install python 3.9.18`
    - And to make it the default: `asdf global python 3.9.18`

The `venv` command at the end will also install a new virtual environment in excursor.  To activate it:

```bash
source venv/bin/activate
```

Then you can install the full excursor dependencies

```bash
poetry install --all-extras --with dev
```

Skip any of the commands above if you already have asdf, poetry, or virtualenv already installed.