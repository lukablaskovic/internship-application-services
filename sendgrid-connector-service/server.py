import sendgrid
import bugsnag

import base64
import os, sys
from sendgrid.helpers.mail import (
    Mail,
    To,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
    ContentId,
    DynamicTemplateData,
)
import requests
from aiohttp import web
import aiohttp_cors
from urllib import parse
from env import *
from datetime import datetime

from env import BUGSNAG

SG = sendgrid.SendGridAPIClient(API_KEY)
# HEADER = {"Authorization": "Bearer "+API_KEY}


routes = web.RouteTableDef()


async def send_email(request, template_type):
    data = await request.json()
    print(data)
    # Ensure that all keys are lowercase
    data = {key.lower(): value for key, value in data.items()}

    if request.query_string:
        query_dict = dict(request.query)
    else:
        # error -> to:email must be send via params
        pass

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=query_dict["to"],
    )

    if template_type == "student_after_approval":
        message.template_id = STUDENT_AFTER_APPROVAL_TEMPLATE
    elif template_type == "student_after_refusal":
        message.template_id = STUDENT_AFTER_REFUSAL_TEMPLATE
    elif template_type == "student_after_allocation":
        message.template_id = STUDENT_AFTER_ALLOCATION_NOTIFICATION_TEMPLATE
    elif template_type == "student_after_return":
        message.template_id = STUDENT_AFTER_RETURN_TEMPLATE
    elif template_type == "poslodavac_after_allocation":
        message.template_id = POSLODAVAC_AFTER_ALLOCATION_NOTIFICATION_TEMPLATE
    elif template_type == "student_potvrda_pdf":
        message.template_id = STUDENT_SEND_PDF_TEMPLATE
    elif template_type == "mentor_potvrda_pdf":
        message.template_id = MENTOR_SEND_PDF_TEMPLATE
    message.dynamic_template_data = DynamicTemplateData(data)

    if "attachment_url" in data:
        file_handle = requests.get(data["attachment_url"])
        encoded_pdf = base64.b64encode(file_handle.content).decode()

        attachment = Attachment()
        attachment.file_content = FileContent(encoded_pdf)
        attachment.file_type = FileType("application/pdf")
        attachment.file_name = FileName(data["attachment_name"])
        attachment.disposition = Disposition("attachment")
        attachment.content_id = ContentId("Example Content ID")

        message.attachment = attachment

    try:
        SG.send(message)
    except Exception as e:
        print(e)


@routes.post("/send/email/pdf/student")
async def send_email_student_pdf(request):
    # Specify template type
    template_type = "student_pdf"

    await send_email(request, template_type, attachment_name="potvrda_prakse.pdf")

    return web.json_response({"status": "OK"})


@routes.post("/email")
async def send_plain_email(request):
    query_dict = dict(request.query)
    await send_email(request, query_dict.get("template"))
    return web.json_response({"status": "OK"})


@routes.get("/status")
async def status_check(request):
    """
    Health check endpoint to monitor the status of the service.
    Returns a 200 status code with a JSON payload if the service is running.
    """
    return web.json_response(
        {
            "microservice": "sendgrid-connector-notification-service",
            "status": "OK",
            "message": "Service is running",
            "status_check_timestamp": datetime.now().isoformat(),
        },
        status=200,
    )


@routes.post("/restart")
async def restart_server(request):
    """
    Handler to restart the server.
    """
    print("Restarting server...")
    os.execv(sys.executable, ["python"] + sys.argv)


app = None

project_root = os.path.dirname(os.path.abspath(__file__))
bugsnag.configure(
    api_key=BUGSNAG,
    project_root=project_root,
)


async def bugsnag_middleware(app, handler):
    async def middleware_handler(request):
        try:
            response = await handler(request)
            return response
        except Exception as e:
            bugsnag.notify(e)
            raise e

    return middleware_handler


def run():
    global app

    app = web.Application(middlewares=[bugsnag_middleware])
    app.add_routes(routes)
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        },
    )

    for route in list(app.router.routes()):
        cors.add(route)

    return app


async def serve():
    return run()


if __name__ == "__main__":
    app = run()
    web.run_app(app, port=8081)

# conda activate sendgrid-connector-service && npx nodemon server.py
