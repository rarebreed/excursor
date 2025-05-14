# excursor

excursor means to scout or spy in latin.  `excursor` is a tool to learn about machine learning from first principles.
This means understanding the math behind how different machine learning models work.  It will focus on Bayesian Neural
Networks (BNN), and specifically Pretrained Fitted Networks (PFN).  Since PFN are also transformers, it will cover them
as well.

It does so with tutorials on math including:

- Linear algebra
    - linear equations and transformations
    - Matrices and 
    - Eigenvalues and vectors
    - spans, SVD and PCA
- Calculus
    - Precalc and kinds of functions
    - Differential Calculus
    - Integral Calculus
    - Vector Calculus
- Probability and statistics
    - Distributions
    - Bayes Theorem and inference
    - Variational Inference
    - Modelling and sampling
- Machine learning
    - Loss/cost/optimization functions
    - softmax
    - cross entropy
    - different activation functions

A capstone project will be to create a BNN that is trained on flaky tests, since flaky tests are probabilistic in nature

As a bonus, we will also cover some other math fields for quantum computing:

- Abstract Algebra
    - groups
    - rings
    - fields
    - homomorphisms and isomorphisms


## Installing 

excursor uses uv as its dependency manager, so the first thing to do is install uv.  Go to their site at

https://docs.astral.sh/uv/getting-started/installation/

and follow the directions according to your operating system.  For linux and mac, it will be simple;

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installing python

With uv, this is very simple and can be done through uv itself

```
uv python install 3.13
```

## Managing virtual environments

uv can also create and manage virtual environments

```bash
uv venv .venv

## For bash or zsh
source .venv/bin/activate
## for nushell
overlay use .venv/bin/activate.nu
##  for powershell
.venv/Scripts/activate.ps1
```

Note that by default, uv expects the virtual environment folder to be named `.venv`.  You can set a different name as an
the environment variable `VIRTUAL_ENV=/path/to/vnv`

Even if you forget to create the .venv, uv will create a .venv for you when you add a dependency

## Using with VS Code

Normally, once VS Code detects a `.venv` folder in your worksace, a messaage will popup prompting if you wish to use it
as your default interpreter.

If it does not, you can do the following.  Open a python file, and select the python interpreter to use with
`CTRL+SHIFT+P` and  then selcting the `Python Select Interpreter` choice.  Then click the `Enter path` option and enter
the path to where the virtual environment folder is. installed the default environment (or dev environment).

Do the same for the Jupyter notebooks.  Click on the `Select Kernel` then `Python Environments` then choose your python interpreter as above.  If you don't see it listed, follow the directions above by opening a python file, and selecting the interpreter.