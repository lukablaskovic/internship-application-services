# Notification service

Example of SendGrid email notifcation service.

## Installation
```
pip install -r requirements.txt
```

You will need to create `env.py` in which you will store your API key, email from which you will send other emails and your templates.

```python
API_KEY = "xxxxxxxxxxxxx"
FROM_EMAIL = "example@email.com"
TEMPLATE_ONE = "XXXXXXXXXXXX"
TEMPLATE_TWO = "XXXXXXXXXXXX"
```

It is also possible to export these keys as environment variables, but I prefer this way...

## Usage

Main function in this SendGrid example is `send_email()` which accepts three arguments _request_, _template\_type_ and _attachment\_name_.

It is expected that inside request there will be querry string **?to=example@email.com** which specifies who will be a recipient of the email. At the moment only one recipient is supported but in the future this will be expanded to accept multiple recipients.

API endpoints must be specified for each template you want to use and inside handlers for before mentioned endpoints you should specify template type you want for your email.

At the moment `send_email()` checks for **attachment** key within JSON request data to send attachment with email. This can be easily adapted to suit your business needs in case of multiple attachments.