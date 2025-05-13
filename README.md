# excursor

excursor means to scout or spy in latin.  excursor is a tool to learn about machine learning from first principles. This
means it will cover the math behind how different machine learning models work.  It will focus on Bayesian Neural
Networks (BNN), and specifically Pretrained Fitted Networks (PFN).  

It does so by tutorials on math including:

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

## Installing 

excursor uses pixi as its dependency manager, so the first thing to do is install pizi.  Go to their site at

https://pixi.sh/latest/

and follow the directions according to your operating system.  For linux and mac, it will be simple;

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

## Using with VS Code

When opening a python file, you can select the python interpreter to use with `CTRL+SHIFT+P` and  then selcting the 
`Python Select Interpreter` choice.  Then click the `Enter path` option and enetr the path to where pixi installed the
default environment (or dev environment).

> this should be in `.pixi\envs\default\python.exe` for windows or `.pixi/envs/default/python3` for linux and mac

Do the same for the Jupyter notebooks.  Click on the `Select Kernel` then `Python Environments` then choose your python interpreter from pixi that was selected earlier.  If you don't see it listed, follow the directions above by opening a
python file, and selecting the interpreter.