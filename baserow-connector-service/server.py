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
    "studenti": "186615",
    "poslodavci": "186616",
    "zadaci-za-odabir": "186618",
    "student-preferencije": "186619",
    "alokacije": "186614",
    "prijavnice": "186620",
    "dnevnici": "186621",
}

client = BaserowClient()


@routes.post("/students")
async def add_student(req):
    print("BASEROW_POST_students\n", req)

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


@routes.delete("/students/email/{value}")
async def delete_student(req):
    print("BASEROW_DELETE_delete_student\n", req)
    value = req.match_info.get("value", None)

    if not value:
        return web.Response(
            text=json.dumps({"error": "Invalid email."}),
            status=400,
            content_type="application/json",
        )
    res = client.delete_row_by_attribute(TABLES_MAP["studenti"], "Email", value)
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
    print("BASEROW_POST_prijava-preferencija\n", req)
    row_data = await req.json()
    res = client.create_row(table_id=TABLES_MAP["student-preferencije"], data=row_data)
    response_data = {}

    if "data" in res:
        student_id = res["data"]["id"]
        student_jmbag = row_data["JMBAG"]
        response_data["student_id"] = student_id

        current_date = dt.datetime.utcnow().isoformat() + "Z"

        alokacija_data = {
            "JMBAG": student_jmbag,
            "Student": [student_jmbag],
            "Datum prijave": current_date,
            "process_instance_id": row_data["id_instance"],
            "frontend_url": row_data["_frontend_url"],
        }

        # Add to Alokacija table
        alokacija_response = client.create_row(
            table_id=TABLES_MAP["alokacije"], data=alokacija_data
        )
        if "data" in alokacija_response:
            response_data["alokacija_id"] = alokacija_response["data"]["id"]
        elif "error" in alokacija_response:
            return web.Response(
                text=json.dumps(alokacija_response["error"]),
                status=alokacija_response["status_code"],
                content_type="application/json",
            )

    return web.Response(text=json.dumps(response_data), content_type="application/json")


@routes.get("/student-preferencije-detailed/{JMBAG}")
async def fetch_student_preferences_detailed(request):
    JMBAG = request.match_info.get("JMBAG", None)

    # If JMBAG is missing, return error
    if not JMBAG:
        return web.Response(
            text=json.dumps({"error": "Missing JMBAG."}),
            status=400,
            content_type="application/json",
        )

    # First get the student preferences
    table_id = TABLES_MAP["student-preferencije"]
    row_id = client.get_row_id_by_attribute(
        table_id, "JMBAG", JMBAG, br.Student_preferencije_Table_Mappings
    )
    if not row_id:
        return web.Response(
            text=json.dumps({"error": "Student not found."}),
            status=404,
            content_type="application/json",
        )

    student_preferences = client.get_row(table_id, row_id)

    if "error" in student_preferences:
        return web.Response(
            text=json.dumps(student_preferences),
            status=student_preferences["status_code"],
            content_type="application/json",
        )

    # Fetch details for each Zadatak
    for preference_key in ["Prvi odabir", "Drugi odabir", "Treći odabir"]:
        preference = student_preferences["data"].get(preference_key)
        if preference:
            zadatak_id = preference[0]["id"] if preference else None
            if zadatak_id:
                zadatak_data = client.get_row(
                    TABLES_MAP["zadaci-za-odabir"], zadatak_id
                )
                preference[0]["details"] = (
                    zadatak_data["data"] if "data" in zadatak_data else None
                )

    return web.Response(
        text=json.dumps(student_preferences),
        content_type="application/json",
    )


@routes.post("/alokacija")
async def alokacija_studenta(request):
    # Parse incoming request data
    data = await request.json()
    student = data.get("Student")
    alocirani_zadatak_id = data.get("Alocirani zadatak")

    if not student or not alocirani_zadatak_id:
        return web.Response(
            text=json.dumps({"error": "Missing JMBAG or Alocirani zadatak"}),
            status=400,
            content_type="application/json",
        )

    # Get the row_id of the student in the "alokacije" table
    table_id = TABLES_MAP["alokacije"]
    row_id = client.get_row_id_by_attribute(table_id, "JMBAG", student[0])

    if not row_id:
        return web.Response(
            text=json.dumps({"error": "Student not found in alokacije."}),
            status=404,
            content_type="application/json",
        )

    # Update the student's Alocirani zadatak
    update_data = {"Alocirani zadatak": [alocirani_zadatak_id]}
    update_response = client.update_row(table_id, row_id, update_data)

    if "error" in update_response:
        return web.Response(
            text=json.dumps(update_response["error"]),
            status=update_response["status_code"],
            content_type="application/json",
        )

    return web.Response(
        text=json.dumps(update_response), content_type="application/json"
    )


@routes.get("/alokacije/public")
async def fetch_public_alokacije(request):
    table_id = TABLES_MAP["alokacije"]

    # Extract the JMBAG value from query parameters
    jmbag = request.query.get("JMBAG", None)

    if jmbag:
        # Get the student alokacija record ID using JMBAG
        row_id = client.get_row_id_by_attribute(
            table_id, "JMBAG", jmbag, br.Alokacija_Table_Mappings
        )

        if not row_id:  # If there's no matching row, return an empty list
            return web.Response(
                text=json.dumps([]),
                content_type="application/json",
            )

        # Fetch the specific student alokacija using row ID
        alokacija_data = client.get_row(table_id, row_id)
        if "error" in alokacija_data:
            return web.Response(
                text=json.dumps(alokacija_data["error"]),
                status=alokacija_data["status_code"],
                content_type="application/json",
            )

        # Return the specific student alokacija
        return web.Response(
            text=json.dumps(alokacija_data["data"]),
            content_type="application/json",
        )
    else:
        # If no JMBAG was provided, fetch all rows
        alokacije_rows = client.get_table_rows(table_id)
        if "error" in alokacije_rows:
            return web.Response(
                text=json.dumps(alokacije_rows["error"]),
                status=alokacije_rows["status_code"],
                content_type="application/json",
            )

        # Return all alokacije
        return web.Response(
            text=json.dumps(alokacije_rows["data"]["results"]),
            content_type="application/json",
        )


# Generic GET route for fetching rows from a table
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
