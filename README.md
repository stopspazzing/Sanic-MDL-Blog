[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a6bd96eca22d4711a708db80a9b42e63) ](https://www.codacy.com/app/stopspazzing/Sanic-Server-with-MDL-Blog-Template?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=stopspazzing/Sanic-Server-with-MDL-Blog-Template&amp;utm_campaign=Badge_Grade)[![Code Issues](https://www.quantifiedcode.com/api/v1/project/317d5f1e01704e5eb221b09ede70b9e7/badge.svg)](https://www.quantifiedcode.com/app/project/317d5f1e01704e5eb221b09ede70b9e7)
# Material Design Lite Blog Using Sanic
A [Sanic](https://github.com/channelcat/sanic) ([asynchronous](http://stackoverflow.com/questions/748175/asynchronous-vs-synchronous-execution-what-does-it-really-mean)) server running with the [blog template](https://getmdl.io/templates/blog/) from [Material Design Lite](https://getmdl.io/) . Eventually will become a 'live' blog template with an [admin dashboard](https://getmdl.io/templates/dashboard/index.html).

## Prerequisites
You need several packages first for all pip packages to completely install.

So here is a list of packages required:
```
python & python-dev >=3.6
unixodbc
unixodbc-dev
libsqliteodbc
```


## Installation

`pip install -r requirements.txt`


## Starting Server

```
NOTICE:

While I have gotten this to work on Windows with Sanic 4.1, this will not run on Windows with Sanic 5+, not by choice, but because required packages for Sanic aren't supported on Windows at this time.
```

To start the server: `python main.py`

To access server: http://127.0.0.1:8000
