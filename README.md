# workflow-test

This is a test repository for GitHub actions, with use of Pyinstaller to create an executable.

## Hello World

The application is made using PyQt, consisting of a single window. In the window, there is a label and a button. The label can be toggled on and off using the button.

You can download the **Hello World** application [here](https://github.com/leorudczenko/workflow-test/releases/latest/download/hello-world.exe).

_Note: When first running the application after download, it will take sometime to start. Please be patient._

You can find the executable for the application in the latest release assets.

## Testing

You can run the tests for the application by running the following:

```bash
export PYTHONPATH=.
pytest -vs test/
```