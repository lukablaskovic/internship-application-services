import aiohttp
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
import tempfile
from dotenv import load_dotenv
import bugsnag

load_dotenv()
routes = aiohttp.web.RouteTableDef()

app = None

TABLES_MAP_DEV = {
    "Student": "186615",
    "Poslodavac": "186616",
    "Zadaci_za_odabir": "186618",
    "Student_preferencije": "186619",
    "Alokacija": "186614",
    "Prijavnica": "186620",
    "Dnevnik_prakse": "186621",
}

TABLES_MAP = {
    "Student": "488",
    "Poslodavac": "489",
    "Zadaci_za_odabir": "490",
    "Student_preferencije": "491",
    "Alokacija": "492",
    "Prijavnica": "493",
    "Dnevnik_prakse": "494",
}


client = BaserowClient()


@routes.post("/api/student")
async def add_new_student(req):
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
        return aiohttp.web.Response(
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
            "avatar": [data.get("avatar")],
        },
    )
    return aiohttp.web.Response(text=json.dumps(res), content_type="application/json")


@routes.delete("/api/student/email/{value}")
async def delete_student(req):
    # print("BASEROW_DELETE_delete_student\n", req)
    value = req.match_info.get("value", None)

    if not value:
        return aiohttp.web.Response(
            text=json.dumps({"error": "Invalid email."}),
            status=400,
            content_type="application/json",
        )
    res = client.delete_row_by_attribute(
        TABLES_MAP["Student"], "email", value, br.Student_Mappings
    )
    return aiohttp.web.Response(text=json.dumps(res), content_type="application/json")


@routes.post("/api/zadaci_za_odabir")
async def add_new_assignment(req):
    data = await req.json()
    # Check if the company exists in the 'Poslodavac' table
    company_name = data.get("Poslodavac")[0]
    existing_company_id = client.get_row_id_by_attribute(
        TABLES_MAP["Poslodavac"], "naziv", company_name, br.Poslodavac_Mappings
    )

    # If company doesn't exist, create a new entry in the 'Poslodavac' table
    if not existing_company_id:
        new_company_data = {"naziv": company_name}
        company_creation_response = client.create_row(
            table_id=TABLES_MAP["Poslodavac"], data=new_company_data
        )
        if "data" in company_creation_response:
            existing_company_id = company_creation_response["data"]["id"]
        else:
            return aiohttp.web.Response(
                text=json.dumps(company_creation_response),
                content_type="application/json",
            )
    new_row_data = dict(
        {
            "Poslodavac": data.get("Poslodavac"),
            "voditelj_odobrio": "u razradi",
            "poslodavac_email": data.get("poslodavac_email"),
            "broj_studenata": data.get("broj_studenata"),
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
            "selekcija": data.get("selekcija"),
            "proces_selekcije": data.get("proces_selekcije"),
        },
    )

    creation_response = client.create_row(TABLES_MAP["Zadaci_za_odabir"], new_row_data)

    # print("creation_response", creation_response)

    if "data" in creation_response:
        new_row_id = creation_response["data"]["id"]

        Poslodavac_value = data.get("Poslodavac")[0] if data.get("Poslodavac") else ""

        formatted_id = f"Zadatak {new_row_id} - {Poslodavac_value}"
        update_response = client.update_row(
            TABLES_MAP["Zadaci_za_odabir"], new_row_id, {"id_zadatak": formatted_id}
        )

        return aiohttp.web.Response(
            text=json.dumps(update_response), content_type="application/json"
        )

    else:
        return aiohttp.web.Response(
            text=json.dumps(creation_response), content_type="application/json"
        )


@routes.post("/api/poslodavac")
async def add_new_company(req):
    data = await req.json()
    company_name = data.get("naziv")

    # Check if the company already exists
    existing_company_id = client.get_row_id_by_attribute(
        "Poslodavac", "naziv", company_name, br.Poslodavac_Mappings
    )
    if existing_company_id:
        return aiohttp.web.Response(
            text=json.dumps({"error": "Company already exists"}),
            content_type="application/json",
        )

    # If company doesn't exist, create a new entry
    new_company_data = {"naziv": company_name}
    creation_response = client.create_row(
        table_id=TABLES_MAP["Poslodavac"], data=new_company_data
    )

    return aiohttp.web.Response(
        text=json.dumps(creation_response), content_type="application/json"
    )


@routes.patch("/api/poslodavac/update")
async def update_company(request):
    try:
        data = await request.json()

        # Extract the naziv and other fields from the data
        naziv = data.get("naziv")
        web = data.get("web")
        direktor = data.get("direktor")
        maticni_broj = data.get("maticni_broj")
        OIB = data.get("OIB")
        adresa = data.get("adresa")

        # Validate that naziv is provided
        if not naziv:
            return aiohttp.web.Response(
                text=json.dumps({"error": "naziv is required."}),
                status=400,
                content_type="application/json",
            )

        # Search for the company with the given naziv in TABLES_MAP["Poslodavac"]
        table_id = TABLES_MAP["Poslodavac"]
        row_id = client.get_row_id_by_attribute(
            table_id, "naziv", naziv, br.Poslodavac_Mappings
        )

        # If company not found, return an error
        if not row_id:
            return aiohttp.web.Response(
                text=json.dumps({"error": "Company not found."}),
                status=404,
                content_type="application/json",
            )

        # Update the company's fields with the provided data
        client.update_row(
            table_id,
            row_id,
            {
                "web": web,
                "direktor": direktor,
                "maticni_broj": maticni_broj,
                "OIB": OIB,
                "adresa": adresa,
            },
        )

        return aiohttp.web.Response(
            text=json.dumps({"message": "Company updated successfully."}),
            status=200,
            content_type="application/json",
        )
    except Exception as e:
        return aiohttp.web.Response(
            text=json.dumps({"error": str(e)}),
            status=500,
            content_type="application/json",
        )


@routes.patch("/api/zadaci_za_odabir/odobrenje")
async def update_voditelj_odobrio(req):
    data = await req.json()

    voditelj_odobrio = data.get("voditelj_odobrio")
    if voditelj_odobrio is None:
        return aiohttp.web.Response(
            status=400, text="Missing 'voditelj_odobrio' in request body."
        )

    id_zadatak = data.get("id_zadatak")
    if not id_zadatak:
        return aiohttp.web.Response(
            status=400, text="Missing 'id_zadatak' in request body."
        )

    row_id = client.get_row_id_by_attribute(
        TABLES_MAP["Zadaci_za_odabir"],
        "id_zadatak",
        id_zadatak,
        br.Zadaci_za_odabir_Mappings,
    )

    try:
        client.update_row(
            TABLES_MAP["Zadaci_za_odabir"],
            row_id,
            {"voditelj_odobrio": voditelj_odobrio},
        )
        return aiohttp.web.Response(status=200, text="Updated successfully.")

    except Exception as e:
        return aiohttp.web.Response(status=402, text=f"Error: {e}")


@routes.post("/api/student_preferencije")
async def register_assignments(req):
    # print("BASEROW_POST_register_assignments\n", req)
    data = await req.json()
    preferencije_data = {
        "id_preferencije": str(uuid.uuid4()),
        "JMBAG": data.get("JMBAG"),
        "Student": [data.get("JMBAG")],
        "Prvi_odabir": data.get("Prvi_odabir"),
        "Drugi_odabir": data.get("Drugi_odabir"),
        "Treci_odabir": data.get("Treci_odabir"),
        "napomena": data.get("napomena"),
    }
    preferencije_response = client.create_row(
        table_id=TABLES_MAP["Student_preferencije"], data=preferencije_data
    )
    response_data = {}

    if "data" in preferencije_response:
        student_id = preferencije_response["data"]["id"]
        Student_preferencije = preferencije_response["data"]["id_preferencije"]
        response_data["student_id"] = student_id
        response_data["id_preferencije"] = Student_preferencije

        current_date = dt.datetime.utcnow().isoformat() + "Z"

        alokacija_data = {
            "id_alokacija": str(uuid.uuid4()),
            "JMBAG": data.get("JMBAG"),
            "Student_preferencije": [Student_preferencije],
            "Student": [data.get("JMBAG")],
            "datum_prijave": current_date,
            "process_instance_id": data["id_instance"] or "",
            "frontend_url": data["_frontend_url"],
        }

        # Add to Alokacija table
        alokacija_response = client.create_row(
            table_id=TABLES_MAP["Alokacija"], data=alokacija_data
        )
        if "data" in alokacija_response:
            response_data["id_alokacija"] = alokacija_response["data"]["id_alokacija"]
        elif "error" in alokacija_response:
            return aiohttp.web.Response(
                text=json.dumps(alokacija_response["error"]),
                status=alokacija_response["status_code"],
                content_type="application/json",
            )

    return aiohttp.web.Response(
        text=json.dumps(response_data), content_type="application/json"
    )


@routes.get("/api/student_preferencije/detailed/{id_preferencije}")
async def fetch_student_preferences_detailed(request):
    id_preferencije = request.match_info.get("id_preferencije", None)

    # If id_alokacija is missing, return error
    if not id_preferencije:
        return aiohttp.web.Response(
            text=json.dumps({"error": "Missing id_preferencije."}),
            status=400,
            content_type="application/json",
        )

    # First get the student preferences
    table_id = TABLES_MAP["Student_preferencije"]
    row_id = client.get_row_id_by_attribute(
        table_id, "id_preferencije", id_preferencije, br.Student_preferencije_Mappings
    )
    # print("FOUND ROW ID", row_id)
    if not row_id:
        return aiohttp.web.Response(
            text=json.dumps({"error": "Student not found."}),
            status=404,
            content_type="application/json",
        )

    student_preferences = client.get_row(table_id, row_id)

    if "error" in student_preferences:
        return aiohttp.web.Response(
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

    return aiohttp.web.Response(
        text=json.dumps(student_preferences),
        content_type="application/json",
    )


@routes.post("/api/alokacija")
async def alokacija_studenta(request):
    # Parse incoming request data
    data = await request.json()
    student = data.get("Student")
    id_alokacija = data.get("id_alokacija")
    # print("id_alokacija ", id_alokacija)
    alocirani_zadatak_id = data.get("Alocirani_zadatak")
    status_zahtjeva = "evaluacija_u_tijeku"

    if not student or not alocirani_zadatak_id:
        return aiohttp.web.Response(
            text=json.dumps({"error": "Missing JMBAG or Alocirani zadatak"}),
            status=400,
            content_type="application/json",
        )

    if not id_alokacija:
        return aiohttp.web.Response(
            text=json.dumps(
                {"error": f"Alokacija ${id_alokacija} not found in Alokacija table."}
            ),
            status=404,
            content_type="application/json",
        )

    update_data = {
        "Alocirani_zadatak": [alocirani_zadatak_id],
        "status_zahtjeva": status_zahtjeva,
    }

    row_id = client.get_row_id_by_attribute(
        TABLES_MAP["Alokacija"], "id_alokacija", id_alokacija, br.Alokacija_Mappings
    )

    update_response = client.update_row(
        table_id=TABLES_MAP["Alokacija"], row_id=row_id, data=update_data
    )
    # print(update_response)

    if "error" in update_response:
        return aiohttp.web.Response(
            text=json.dumps(update_response["error"]),
            status=update_response["status_code"],
            content_type="application/json",
        )

    return aiohttp.web.Response(
        text=json.dumps(update_response), content_type="application/json"
    )


@routes.patch("/api/status_zahtjeva")
async def update_status_zahtjeva(request):
    data = await request.json()

    table_id = TABLES_MAP["Alokacija"]

    id_alokacija = data.get("id_alokacija")
    novi_status_zahtjeva = data.get("status_zahtjeva")

    row_id = client.get_row_id_by_attribute(
        table_id, "id_alokacija", id_alokacija, br.Alokacija_Mappings
    )
    if not row_id:
        return aiohttp.web.Response(
            text=json.dumps(None), content_type="application/json"
        )

    update_response = client.update_row(
        table_id, row_id, {"status_zahtjeva": novi_status_zahtjeva}
    )

    if "error" in update_response:
        return aiohttp.web.Response(
            text=json.dumps(update_response["error"]),
            status=update_response["status_code"],
            content_type="application/json",
        )

    return aiohttp.web.Response(
        text=json.dumps(update_response), content_type="application/json"
    )


@routes.get("/api/alokacija/public")
async def fetch_public_alokacije(request):
    table_id = TABLES_MAP["Alokacija"]

    # Extract the id_alokacija value from query parameters
    id_alokacija = request.query.get("id_alokacija", None)

    def format_output(row):
        zadatak_details = None
        try:
            zadatak_id = row.get("Alocirani_zadatak", None)

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
            "id_alokacija": row.get("id_alokacija", ""),
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
            "status_zahtjeva": row.get("status_zahtjeva", ""),
            "popunjena_prijavnica": row.get("popunjena_prijavnica", ""),
            "predan_dnevnik_prakse": row.get("predan_dnevnik_prakse", ""),
        }

    if id_alokacija is not None:
        # print("id_alokacija", id_alokacija)
        # Get the student alokacija record ID using JMBAG
        row_id = client.get_row_id_by_attribute(
            table_id, "id_alokacija", id_alokacija, br.Alokacija_Mappings
        )

        if not row_id:
            return aiohttp.web.Response(
                text=json.dumps(None), content_type="application/json"
            )

        # Fetch the specific student alokacija using row ID
        alokacija_data = client.get_row(table_id, row_id)
        if "error" in alokacija_data:
            return aiohttp.web.Response(
                text=json.dumps(alokacija_data["error"]),
                status=alokacija_data["status_code"],
                content_type="application/json",
            )

        # Return the specific student alokacija
        return aiohttp.web.Response(
            text=json.dumps(format_output(alokacija_data["data"])),
            content_type="application/json",
        )

    else:
        # If no JMBAG was provided, fetch all rows
        alokacije_rows = client.get_table_rows(table_id)
        if "error" in alokacije_rows:
            return aiohttp.web.Response(
                text=json.dumps(alokacije_rows["error"]),
                status=alokacije_rows["status_code"],
                content_type="application/json",
            )
        if not alokacije_rows["data"]:
            return aiohttp.web.Response(
                text=json.dumps({"message": "Nema podataka."}),
                status=404,
                content_type="application/json",
            )

        # Format and return all alokacije
        results = [format_output(row) for row in alokacije_rows["data"]["results"]]
        return aiohttp.web.Response(
            text=json.dumps(results), content_type="application/json"
        )


@routes.post("/api/prijavnica")
async def fill_application_form(request):
    data = await request.json()

    prijavnica_data = {
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
        "id_prijavnica": str(uuid.uuid4()),
        "Alokacija": [data["id_alokacija"]],
        "process_instance_id": data["id_instance"],
    }

    prijavnica_response = client.create_row(TABLES_MAP["Prijavnica"], prijavnica_data)

    if "error" in prijavnica_response:
        return aiohttp.web.Response(
            text=json.dumps(prijavnica_response["error"]),
            status=prijavnica_response["status_code"],
            content_type="application/json",
        )

    id_alokacija = data["id_alokacija"]

    if not id_alokacija:
        return aiohttp.web.Response(
            text=json.dumps(
                {"error": f"Alokacija ID ${id_alokacija} not found in Alokacija table."}
            ),
            status=404,
            content_type="application/json",
        )

    update_data = {"popunjena_prijavnica": True}

    row_id = client.get_row_id_by_attribute(
        TABLES_MAP["Alokacija"], "id_alokacija", id_alokacija, br.Alokacija_Mappings
    )

    update_response = client.update_row(TABLES_MAP["Alokacija"], row_id, update_data)

    if "error" in update_response:
        return aiohttp.web.Response(
            text=json.dumps(update_response["error"]),
            status=update_response["status_code"],
            content_type="application/json",
        )

    dnevnik_data = {
        "id_dnevnik_prakse": str(uuid.uuid4()),
        "Alokacija": [data["id_alokacija"]],
        "Student": [data["Student"][0]],
        "id_prijavnica": [prijavnica_data["id_prijavnica"]],
        "process_instance_id": data["id_instance"],
    }

    dnevnik_response = client.create_row(TABLES_MAP["Dnevnik_prakse"], dnevnik_data)

    if "error" in dnevnik_response:
        return aiohttp.web.Response(
            text=json.dumps(dnevnik_response["error"]),
            status=dnevnik_response["status_code"],
            content_type="application/json",
        )

    return aiohttp.web.Response(
        text=json.dumps(
            {
                "id_prijavnica": prijavnica_data["id_prijavnica"],
                "id_dnevnik_prakse": dnevnik_data["id_dnevnik_prakse"],
            }
        ),
        content_type="application/json",
    )


@routes.post("/api/dnevnik")
async def update_dnevnik(request):
    data = await request.json()

    id_dnevnik_prakse = data.get("id_dnevnik_prakse")
    nastavak_radnog_odnosa = data.get("nastavak_radnog_odnosa")
    prijavljen_rok = data.get("prijavljen_rok")

    if (
        not id_dnevnik_prakse
        or nastavak_radnog_odnosa is None
        or prijavljen_rok is None
    ):
        return aiohttp.web.Response(
            text=json.dumps({"error": "Incomplete data."}),
            status=400,
            content_type="application/json",
        )

    table_id = TABLES_MAP["Dnevnik_prakse"]
    row_id = client.get_row_id_by_attribute(
        table_id, "id_dnevnik_prakse", id_dnevnik_prakse, br.Dnevnik_prakse_Mappings
    )

    if not row_id:
        return aiohttp.web.Response(
            text=json.dumps({"error": "Dnevnik prakse not found."}),
            status=404,
            content_type="application/json",
        )

    update_data = {
        "nastavak_radnog_odnosa": nastavak_radnog_odnosa,
        "prijavljen_rok": prijavljen_rok,
    }
    update_response = client.update_row(table_id, row_id, update_data)

    if "error" in update_response:
        return aiohttp.web.Response(
            text=json.dumps(update_response["error"]),
            status=update_response["status_code"],
            content_type="application/json",
        )

    id_alokacija = data.get("id_alokacija")
    row_id = client.get_row_id_by_attribute(
        TABLES_MAP["Alokacija"], "id_alokacija", id_alokacija, br.Alokacija_Mappings
    )

    if not row_id:
        return aiohttp.web.Response(
            text=json.dumps(
                {
                    "error": f"Student ${data['id_instance'],} not found in Alokacija table."
                }
            ),
            status=404,
            content_type="application/json",
        )

    update_data = {"predan_dnevnik_prakse": True}
    update_response = client.update_row(TABLES_MAP["Alokacija"], row_id, update_data)

    if "error" in update_response:
        return aiohttp.web.Response(
            text=json.dumps(update_response["error"]),
            status=update_response["status_code"],
            content_type="application/json",
        )

    return aiohttp.web.Response(
        text=json.dumps(update_response), content_type="application/json"
    )


# Generic GET route for fetching rows from a table
@routes.get("/api/{table_name}")
async def fetch_table_rows(request):
    queryParams = []

    table_name = request.match_info.get("table_name", None).capitalize()
    if not table_name or table_name not in TABLES_MAP:
        return aiohttp.web.Response(
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
            return aiohttp.web.Response(
                text=json.dumps(row_data["error"]),
                status=row_data["status_code"],
                content_type="application/json",
            )
        return aiohttp.web.Response(
            text=json.dumps(row_data), content_type="application/json"
        )

    rows = client.get_table_rows(table_id, queryParams)
    if "error" in rows:
        return aiohttp.web.Response(
            text=json.dumps(rows["error"]),
            status=rows["status_code"],
            content_type="application/json",
        )
    return aiohttp.web.Response(text=json.dumps(rows), content_type="application/json")


@routes.post("/api/direct-file-upload")
async def direct_upload_to_baserow(request):
    # print("request", request)
    reader = await request.multipart()

    field = await reader.next()

    assert field.name == "file"
    file_content = await field.read(decode=True)
    file_name = field.filename

    temp_dir = tempfile.gettempdir()
    temp_filepath = os.path.join(temp_dir, file_name)

    with open(temp_filepath, "wb") as tmpfile:
        tmpfile.write(file_content)

    try:
        upload_result = client.upload_file(temp_filepath)

        os.remove(temp_filepath)

        if "error" in upload_result:
            return aiohttp.web.Response(
                text=str(upload_result["error"]),
                status=upload_result.get("status_code", 500),
            )
        else:
            return aiohttp.web.Response(text=json.dumps(upload_result), status=200)

    except Exception as e:
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return aiohttp.web.Response(text=f"An error occurred: {str(e)}", status=500)


# Store files on Baserow server
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
        return aiohttp.web.json_response(response)

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
    # print("row_id", row_id)

    if not row_id:
        return aiohttp.web.json_response({"error": "Row not found."}, status=404)

    result = client.update_row(table_id, row_id, baserow_data)
    # print("result from store_file_in_baserow:", result)
    return aiohttp.web.json_response(result)


@routes.post("/api/upload/student-avatar/{JMBAG}")
async def store_student_avatar(request):
    jmbag = request.match_info.get("JMBAG")
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


@routes.post("/api/upload/pdf-dnevnik/{id_dnevnik_prakse}")
async def store_pdf_dnevnik_prakse(request):
    id_dnevnik_prakse = request.match_info.get("id_dnevnik_prakse")
    return await store_file_in_baserow(
        request,
        TABLES_MAP["Dnevnik_prakse"],
        "id_dnevnik_prakse",
        id_dnevnik_prakse,
        br.Dnevnik_prakse_Mappings,
        "dnevnik_prakse_upload",
    )


@routes.post("/api/upload/pdf-ispunjena-potvrda/{id_dnevnik_prakse}")
async def store_pdf_ispunjena_potvrda(request):
    id_dnevnik_prakse = request.match_info.get("id_dnevnik_prakse")
    return await store_file_in_baserow(
        request,
        TABLES_MAP["Dnevnik_prakse"],
        "id_dnevnik_prakse",
        id_dnevnik_prakse,
        br.Dnevnik_prakse_Mappings,
        "ispunjena_potvrda_upload",
    )


@routes.get("/status")
async def status_check(request):
    """
    Health check endpoint to monitor the status of the service.
    Returns a 200 status code with a JSON payload if the service is running.
    """
    return aiohttp.web.json_response(
        {
            "microservice": "sendgrid-connector-notification-service",
            "status": "OK",
            "message": "Service is running",
            "status_check_timestamp": datetime.now().isoformat(),
        },
        status=200,
    )


project_root = os.path.dirname(os.path.abspath(__file__))
bugsnag.configure(
    api_key=os.getenv("BCS_BUGSNAG"),
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

    app = aiohttp.web.Application(middlewares=[bugsnag_middleware])
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
    aiohttp.web.run_app(app, port=os.getenv("PORT", 8081))

# conda activate baserow-connector-service && npx nodemon server.py
