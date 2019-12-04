# Overview
This files are adapted ones for the older libraries using python 2 for the RFID terminal
RC522 Module. Currently an older checkout branch of the `SPI-Pi` Library is used (before Feb 2019) since newer updates occour in an error
with the MFRC522 class. Best way to do this is:

```
git clone https://github.com/lthiery/SPI-Py.git
cd SPI-Py
git checkout -b 8cce26b9ee6e69eb041e9d5665944b88688fca68
sudo python setup.py install
sudo python3 setup.py install
```

In addition there is some UI logic for a terminal, using PyQt5 to read and write the tags on the chip.
It can easily be run on the Pi, touch functionality is build in.