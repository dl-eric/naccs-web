# NACCS website
![](https://img.shields.io/website-up-down-green-red/http/naccs.azurewebsites.net.svg?style=flat)

This is the official repository for the North American Collegiate Counter-Strike website!

Master branch should ALWAYS be production ready. Master is set up with Azure App Service Kudu, and CD is triggered upon every commit (for now).

## Local Deployment

Make sure you have the following environmental variables:

- AWS_COGNITO_CLIENT_ID

- AWS_COGNITO_POOL_ID

- AWS_DEFAULT_REGION

- FLASK_SECRET_KEY

The AWS keys are AWS Cognito dependent. The Flask key can be anything, just make it secure! 

An example of setting an environment variable to your shell is
```
export FLASK_SECRET_KEY="Super secret and secure key!"
```

Once you have your variables set up, move on.

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
