# trap-controller-micro-py

## Tools

The tool scripts use `rshell` so make sure that is installed before using these scripts.

### mp-upload
`mp-upload` is a script to delete everything on the board, upload new code then run that code on the device.
It is given one directory as an argument.

In that directory there should be a `pyboard` folder. The contents of that folder will be uploaded to the device.

That directory can aslo include a `pre-scripts.py` file. This will get run before uploading the contents of `pyboard`.

After the code has been uploaded it will connect to the board and run `main.py`.

When connected to the board you can press:
- CTRL-X to disconnect from the device and exit back to the terminal.
- CTRL-D for a soft reboot, this will run `main.py` again.
- CTRL-C to stop the code from running and get a python terminal on the device.

### mp-test //TODO
`mp-test` is used to run test code on the device.

### mp-connect //TODO
`mp-connect` is used to connect to a device so you can monitor the logs.