# Setup
## Install Packages
```bash
sudo apt install librtlsdr-dev python3-venv
```

## Initialize python virtual environment
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

# Running
```bash
./hello_rtl.py
```

You can then follow the prompts on the terminal to tune the receiver
