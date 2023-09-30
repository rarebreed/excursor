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

You can also run the commands all at once, but on the first run through, it is recommended to install each one at a time

```bash
python3 -m excursor.core.installer sys asdf poetry venv
```

Once all the features are installed, you can install the full excursor dependencies using `poetry`

```bash
poetry install --all-extras --with dev
```

Skip any of the commands above if you already have asdf, poetry, or virtualenv already installed.

## Uninstalling a feature

You can also uninstall a feature by appending with a `-c` or `--clean` at the end.  It is recommended to uninstall in
the reverse order as above (eg, clean venv, then poetry, then asdf)

```bash
python3 -m excursor.core.installer venv poetry asdf -c
```