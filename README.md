# NACCS website
![](https://img.shields.io/website-up-down-green-red/http/naccs.azurewebsites.net.svg?style=flat)

This is the official repository for the North American Collegiate Counter-Strike website!

Master branch should ALWAYS be production ready. Master is set up with Azure App Service Kudu, and CD is triggered upon every commit (for now).

## Local Deployment

*We are using a virtual environment to contain our dependencies.

Linux:
Clone the repository and go into the root folder.

```
# In Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
FLASK_APP=app.py flask run
```

From there, the Flask app should be running on localhost:5000.

## Contribution

tbd
