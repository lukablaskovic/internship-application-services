from aiohttp import web
import asyncio
import uuid
from urllib import parse
import os
import aiohttp_cors
import datetime as dt
import baserow as br
import json
from baserow import BaserowClient
import os, sys
from datetime import datetime

routes = web.RouteTableDef()

app = None

TABLES_MAP = {
    "Student": "186615",
    "Poslodavac": "186616",
    "Zadaci_za_odabir": "186618",
    "Student_preferencije": "186619",
    "Alokacija": "186614",
    "Prijavnica": "186620",
    "Dnevnik_prakse": "186621",
}


client = BaserowClient()


@routes.post("/api/student")
async def add_new_student(req):
    print("BASEROW_POST_students\n", req)

    data = await req.json()

    jmbag = data.get("JMBAG")
    email = data.get("email")

    existing_jmbag = client.get_row_id_by_attribute(
        TABLES_MAP["Student"], "JMBAG", jmbag, br.Student_Mappings
    )
    existing_email = client.get_row_id_by_attribute(
        TABLES_MAP["Student"], "email", email, br.Student_Mappings
    )

    if existing_jmbag or existing_email:
        return web.Response(
            text=json.dumps(
                {
                    "error": "Student s unesenim JMBAG-om ili emailom već postoji",
                    "status_code": 400,
                }
            ),
            content_type="application/json",
            status=400,
        )

    res = client.create_row(
        TABLES_MAP["Student"],
        {
            "JMBAG": data.get("JMBAG"),
            "ime": data.get("ime"),
            "prezime": data.get("prezime"),
            "email": data.get("email"),
            "godina_studija": data.get("godina_studija"),
        },
    )
    return web.Response(text=json.dumps(res), content_type="application/json")


@routes.delete("/api/student/email/{value}")
async def delete_student(req):
    print("BASEROW_DELETE_delete_student\n", req)
    value = req.match_info.get("value", None)

    if not value:
        return web.Response(
            text=json.dumps({"error": "Invalid email."}),
            status=400,
            content_type="application/json",
        )
    res = client.delete_row_by_attribute(
        TABLES_MAP["Student"], "email", value, br.Student_Mappings
    )
    return web.Response(text=json.dumps(res), content_type="application/json")


@routes.post("/api/zadaci_za_odabir")
async def add_new_assignment(req):
    data = await req.json()
    new_row_data = dict(
        {
            "Poslodavac": data.get("Poslodavac"),
            "poslodavac_email": data.get("poslodavac_email"),
            "opis_zadatka": data.get("opis_zadatka"),
            "preferirane_tehnologije": data.get("preferirane_tehnologije"),
            "potrebno_imati": data.get("potrebno_imati"),
            "trajanje_sati": data.get("trajanje_sati"),
            "preferencije_za_studenta": data.get("preferencije_za_studenta"),
            "lokacija": data.get("lokacija"),
            "zeljeno_okvirno_vrijeme_pocetka": data.get(
                "zeljeno_okvirno_vrijeme_pocetka"
            ),
            "angazman_fipu": data.get("angazman_fipu"),
            "napomena": data.get("napomena"),
            "seleckija": data.get("selekcija"),
            "proces_selekcije": data.get("proces_selekcije"),
        },
    )

    creation_response = client.create_row(TABLES_MAP["Zadaci_za_odabir"], new_row_data)

    if "data" in creation_response:
        new_row_id = creation_response["data"]["id"]

        poduzece_value = data.get("poduzece")[0] if data.get("poduzece") else ""

        formatted_id = f"Zadatak {new_row_id} - {poduzece_value}"
        update_response = client.update_row(
            TABLES_MAP["Zadaci_za_odabir"], new_row_id, {"id_zadatak": formatted_id}
        )

        return web.Response(
            text=json.dumps(update_response), content_type="application/json"
        )

    else:
        return web.Response(
            text=json.dumps(creation_response), content_type="application/json"
        )


@routes.post("/api/student_preferencije")
async def register_assignments(req):
    print("BASEROW_POST_register_assignments\n", req)
    row_data = await req.json()
    res = client.create_row(table_id=TABLES_MAP["Student_preferencije"], data=row_data)
    response_data = {}

    if "data" in res:
        student_id = res["data"]["id"]
        student_jmbag = row_data["JMBAG"]
        response_data["student_id"] = student_id

        current_date = dt.datetime.utcnow().isoformat() + "Z"

        alokacija_data = {
            "JMBAG": student_jmbag,
            "Student": [student_jmbag],
            "datum_prijave": current_date,
            "process_instance_id": row_data["id_instance"] or "",
            "frontend_url": row_data["_frontend_url"],
        }

        # Add to Alokacija table
        alokacija_response = client.create_row(
            table_id=TABLES_MAP["Alokacija"], data=alokacija_data
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


@routes.get("/api/student_preferencije/detailed/{JMBAG}")
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
    table_id = TABLES_MAP["Student_preferencije"]
    row_id = client.get_row_id_by_attribute(
        table_id, "JMBAG", JMBAG, br.Student_preferencije_Mappings
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
    for preference_key in ["Prvi_odabir", "Drugi_odabir", "Treci_odabir"]:
        preference = student_preferences["data"].get(preference_key)
        if preference:
            zadatak_id = preference[0]["id"] if preference else None
            if zadatak_id:
                zadatak_data = client.get_row(
                    TABLES_MAP["Zadaci_za_odabir"], zadatak_id
                )
                preference[0]["details"] = (
                    zadatak_data["data"] if "data" in zadatak_data else None
                )

    return web.Response(
        text=json.dumps(student_preferences),
        content_type="application/json",
    )


@routes.post("/api/alokacija")
async def alokacija_studenta(request):
    # Parse incoming request data
    data = await request.json()
    student = data.get("Student")
    alocirani_zadatak_id = data.get("Alocirani_zadatak")

    if not student or not alocirani_zadatak_id:
        return web.Response(
            text=json.dumps({"error": "Missing JMBAG or Alocirani zadatak"}),
            status=400,
            content_type="application/json",
        )

    table_id = TABLES_MAP["Alokacija"]
    row_id = client.get_row_id_by_attribute(
        table_id, "JMBAG", student[0], br.Alokacija_Mappings
    )

    if not row_id:
        return web.Response(
            text=json.dumps(
                {"error": f"Student ${student[0]} not found in Alokacija table."}
            ),
            status=404,
            content_type="application/json",
        )

    update_data = {"Alocirani_zadatak": [alocirani_zadatak_id]}
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


@routes.get("/api/alokacija/public")
async def fetch_public_alokacije(request):
    table_id = TABLES_MAP["Alokacija"]

    # Extract the JMBAG value from query parameters
    JMBAG = request.query.get("JMBAG", None)
    print(JMBAG)

    def format_output(row):
        zadatak_details = None
        try:
            zadatak_id = row.get("Alocirani_zadatak", None)
            print("zadatak_id", zadatak_id)

            if zadatak_id and len(zadatak_id) > 0:
                zadatak_data = client.get_row(
                    TABLES_MAP["Zadaci_za_odabir"], zadatak_id[0]["id"]
                )

                if "data" in zadatak_data:
                    zadatak_details = zadatak_data["data"]
            else:
                print("zadatak_id is None or empty")

        except Exception as e:
            print(f"Error occurred: {e}")

        return {
            "JMBAG": row.get("JMBAG", ""),
            "Alocirani_zadatak": zadatak_id[0]["value"]
            if zadatak_id and len(zadatak_id) > 0
            else None,
            "opis_zadatka": zadatak_details.get("opis_zadatka")
            if zadatak_details
            else None,
            "poslodavac_email": zadatak_details.get("poslodavac_email")
            if zadatak_details
            else None,
            "poslodavac_naziv": zadatak_details.get("Poslodavac")[0]["value"]
            if zadatak_details
            else None,
            "popunjena_prijavnica": row.get("popunjena_prijavnica", ""),
            "predan_dnevnik_prakse": row.get("predan_dnevnik_prakse", ""),
        }

    if JMBAG is not None:
        print("JMBAG", JMBAG)
        # Get the student alokacija record ID using JMBAG
        row_id = client.get_row_id_by_attribute(
            table_id, "JMBAG", JMBAG, br.Alokacija_Mappings
        )

        if not row_id:
            return web.Response(text=json.dumps(None), content_type="application/json")

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
            text=json.dumps(format_output(alokacija_data["data"])),
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
        if not alokacije_rows["data"]:
            return web.Response(
                text=json.dumps({"message": "Nema podataka."}),
                status=404,
                content_type="application/json",
            )

        # Format and return all alokacije
        results = [format_output(row) for row in alokacije_rows["data"]["results"]]
        return web.Response(text=json.dumps(results), content_type="application/json")


@routes.post("/api/prijavnica")
async def fill_application_form(request):
    data = await request.json()

    row_data = {
        "Student": [data["Student"][0]],
        "student_OIB": data["student_OIB"],
        "student_broj_mobitela": data["student_broj_mobitela"],
        "student_email": data["student_email"],
        "mentor_ime": data["mentor_ime"],
        "mentor_prezime": data["mentor_prezime"],
        "mentor_email": data["mentor_email"],
        "detaljan_opis_zadatka": data["detaljan_opis_zadatka"],
        "dogovoreni_broj_sati": data["dogovoreni_broj_sati"],
        "pocetak_prakse": data["pocetak_prakse"],
        "kraj_prakse": data["kraj_prakse"],
        "alokacija_potvrda": data["alokacija_potvrda"],
        "kontakt_potvrda": data["kontakt_potvrda"],
        "Poslodavac": [data["Poslodavac"]],
        "mjesto_izvrsavanja": data["mjesto_izvrsavanja"],
        "id_prijavnica": str(uuid.uuid4()),  # Generate a UUID for id_prijavnica
    }

    response = client.create_row(TABLES_MAP["Prijavnica"], row_data)

    if "error" in response:
        return web.Response(
            text=json.dumps(response["error"]),
            status=response["status_code"],
            content_type="application/json",
        )

    return web.Response(
        text=json.dumps({"id_prijavnica": row_data["id_prijavnica"]}),
        content_type="application/json",
    )


# Generic GET route for fetching rows from a table
@routes.get("/api/{table_name}")
async def fetch_table_rows(request):
    queryParams = []

    table_name = request.match_info.get("table_name", None).capitalize()
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


@routes.post("/api/file-upload")
async def upload_to_baserow(request):
    if "Content-Type" not in request.headers:
        return {"error": "Content-Type header not present."}, 400

    reader = await request.multipart()
    field = await reader.next()
    assert field.name == "file"

    # Generate a unique filename using UUID
    filename = f"{uuid.uuid4()}_{field.filename}"
    file_content = await field.read(decode=True)

    # Save the file to a temporary location first
    with open(filename, "wb") as f:
        f.write(file_content)

    loop = asyncio.get_event_loop()
    client = BaserowClient()
    response = await loop.run_in_executor(None, client.upload_file, filename)

    os.remove(filename)

    # Return the response data and status
    return response, 200


async def store_file_in_baserow(
    request, table_id, field_name, field_value, table_mappings, file_field_name
):
    # Upload the file to Baserow
    response, status = await upload_to_baserow(request)
    # Check if the upload was successful
    if status != 200:
        return web.json_response(response)

    # Get the URL of the uploaded file
    file_data = response["data"]
    baserow_data = {
        file_field_name: [
            {
                "url": file_data["url"],
                "thumbnails": file_data["thumbnails"],
                "name": file_data["name"],
                "size": file_data["size"],
                "mime_type": file_data["mime_type"],
                "is_image": file_data["is_image"],
                "image_width": file_data["image_width"],
                "image_height": file_data["image_height"],
                "uploaded_at": file_data["uploaded_at"],
            }
        ]
    }

    client = BaserowClient()
    row_id = client.get_row_id_by_attribute(
        table_id, field_name, field_value, table_mappings
    )
    print("row_id", row_id)
    print(
        "table_id",
        table_id,
    )
    if not row_id:
        return web.json_response({"error": "Row not found."}, status=404)

    result = client.update_row(table_id, row_id, baserow_data)
    print("result from store_file_in_baserow:", result)
    return web.json_response(result)


@routes.post("/api/upload/student-avatar/{JMBAG}")
async def store_student_avatar(request):
    jmbag = request.match_info.get("JMBAG")
    print(jmbag)
    return await store_file_in_baserow(
        request, TABLES_MAP["Student"], "JMBAG", jmbag, br.Student_Mappings, "avatar"
    )


@routes.post("/api/upload/poslodavac-logo/{naziv}")
async def store_poslodavac_logo(request):
    naziv = request.match_info.get("naziv")
    return await store_file_in_baserow(
        request,
        TABLES_MAP["Poslodavac"],
        "naziv",
        naziv,
        br.Poslodavac_Mappings,
        "logo",
    )


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
