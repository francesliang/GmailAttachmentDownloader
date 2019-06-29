### Gmail Attachment Downloader

This project 

#### Setup
1. Turn on the Gmail API for your Google account, see [this page](https://developers.google.com/gmail/api/quickstart/python).

2. Create a virtual environment under project root directory by running:

```
virtualenv gvenv
```

3. Activate the virtual environment and install dependencies under project root directory:

```
source gvenv/bin/activate
pip3 install -r requirements.txt
```

#### Run
The usage of the script is:
```
usage: downloader.py [-h] Q D

Arguments for downloader

positional arguments:
  Q           Query to filter emails
  D           Directory path to store downloaded attachment files

optional arguments:
  -h, --help  show this help message and exit
```
An example to run:

```
python3 downloader.py "from:example@gmail.com" "/path/to/outputs"
```

