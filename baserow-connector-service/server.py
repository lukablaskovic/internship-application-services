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


@routes.post("/students")
async def add_student(req):
    data = await req.json()
    res = client.create_row(
        TABLES_MAP["studenti"],
        {
            "JMBAG": data.get("jmbag"),
            "Ime": data.get("name"),
            "Prezime": data.get("surname"),
            "Email": data.get("email"),
            "Godina studija": data.get("year_of_study"),
        },
    )
    return web.Response(text=json.dumps(res), content_type="application/json")


@routes.post("/prijava-zadatka")
async def prijava_novog_zadatka(req):
    data = await req.json()
    new_row_data = dict(
        {
            "Poduzeće": data.get("poduzece"),
            "Kontakt email": data.get("kontakt_email"),
            "Zadatak studenta": data.get("zadatak_studenta"),
            "Preferirane tehnologije": data.get("preferirane_tehnologije"),
            "Potrebno imati": data.get("potrebno_imati"),
            "Trajanje (sati)": data.get("trajanje"),
            "Preferencije za studenta": data.get("preferencije_za_studenta"),
            "Lokacija": data.get("lokacija"),
            "Željeno okvirno vrijeme početka": data.get(
                "zeljeno_okvirno_vrijeme_pocetka"
            ),
            "Angažman FIPU": data.get("angazman_fipu"),
            "Napomena": data.get("napomena"),
            "Selekcija": data.get("selekcija"),
            "Proces selekcije": data.get("proces_selekcije"),
        },
    )

    creation_response = client.create_row(TABLES_MAP["zadaci-za-odabir"], new_row_data)

    if "data" in creation_response:
        new_row_id = creation_response["data"]["id"]

        poduzece_value = data.get("poduzece")[0] if data.get("poduzece") else ""

        formatted_id = f"Zadatak {new_row_id} - {poduzece_value}"
        update_response = client.update_row(
            TABLES_MAP["zadaci-za-odabir"], new_row_id, {"ID Zadatka": formatted_id}
        )

        return web.Response(
            text=json.dumps(update_response), content_type="application/json"
        )

    else:
        return web.Response(
            text=json.dumps(creation_response), content_type="application/json"
        )


@routes.post("/prijava-preferencija")
async def prijava_preferencija(req):
    row_data = await req.json()
    res = client.create_row(table_id=TABLES_MAP["student-preferencije"], data=row_data)
    return web.Response(text=json.dumps(res), content_type="application/json")


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

    row_id = request.rel_url.query.get("id")
    if row_id:
        row_data = client.get_row(table_id, row_id)
        if "error" in row_data:
            return web.Response(
                text=json.dumps(row_data["error"]),
                status=row_data["status_code"],
                content_type="application/json",
            )
        return web.Response(text=json.dumps(row_data), content_type="application/json")

    rows = client.get_table_rows(table_id, queryParams)
    if "error" in rows:
        return web.Response(
            text=json.dumps(rows["error"]),
            status=rows["status_code"],
            content_type="application/json",
        )
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

# conda activate baserow-connector-service
# npx nodemon server.py
