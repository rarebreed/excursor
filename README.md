# excursor

excursor means to scout or spy in latin.  excursor is a tool to learn python, mojo, and machine learning. It does so by
building up some projects and notebooks to introduce concepts

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