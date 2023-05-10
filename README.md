# Setup
## Install Packages
```bash
sudo apt install librtlsdr-dev python3-venv
```

### Alma 8
```shell
pip install --upgrade pip
sudo dnf install portaudio python3-tkinter
```
ahh

## Initialize python virtual environment
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install --upgrade pip
pip3 install -r requirements.txt
```

# Running Spectrogram
```bash
./hello_rtl.py
```
You can then follow the prompts on the terminal to tune the receiver

# Running minimal FM chain
```bash
rtl_sdr -f 104.7M -s 256k - | python3 minimal_fm.py | sox -t raw -r 256000 -b 16 -c 1 -L -e signed-integer - -d rate 32000
```

