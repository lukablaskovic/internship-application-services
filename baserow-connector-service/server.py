from aiohttp import web
import requests
from urllib import parse
import os
import aiohttp_cors
import datetime as dt
import baserow as br
import json
from baserow import BaserowClient

routes = web.RouteTableDef()

app = None

TABLES_MAP = {
    "studenti": "186615",  # HARDKODIRANO
    "firme": "186616",
    "zadaci-za-odabir": "186618",
    "student-preferencije": "186619",
    "prijavnice": "186620",
    "dnevnici": "186621",
}

client = BaserowClient()


@routes.post("/studenti")
async def add_student(request):
    data = await request.json()
    response = client.create_row(
        "186615",
        {
            "JMBAG": data.get("_jmbag"),
            "Ime": data.get("ime"),
            "Prezime": data.get("prezime"),
            "Godina studija": data.get("godina_studija"),
        },
    )
    return web.Response(text=json.dumps(response), content_type="application/json")


@routes.get("/{table_name}")
async def fetch_table_rows(request):
    queryParams = []

    table_name = request.match_info.get("table_name", None)
    if not table_name or table_name not in TABLES_MAP:
        return web.Response(
            text=json.dumps({"error": "Invalid table name."}),
            status=400,
            content_type="application/json",
        )
    table_id = TABLES_MAP[table_name]

    search = request.rel_url.query.get("search")
    if search:
        queryParams.append(f"search={search}")

    rows = client.get_table_rows(table_id, queryParams)
    return web.Response(text=json.dumps(rows), content_type="application/json")


def run():
    global app

    app = web.Application()
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
    web.run_app(app, port=8080)

# npx nodemon server.py
