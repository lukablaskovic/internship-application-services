# Airtable connector service

Service is example of API for interactions with Airtable DB.

## Installation
```
pip install -r requirements.txt
```

You will need to create `env.py` in which you will store your API key and Base ID (your database id)

```python
API_KEY = "xxxxxxxxxxxxx"
BASE_ID = "xxxxxxxxxxxxx"
```

It is also possible to export these keys as environment variables, but I prefer this way...

### Note

At the moment CORS is setup to allow all traffic but in the production environment this would need to be modify to only allow specific traffic for each endpoint.

> As each DB is case specific so is this example.