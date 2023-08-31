"""
    // normal fields are in lower_case
    // table references fields are in Upper_case
    // Exception: JMBAG, OIB, ID
    
    // Why all this? Because baserow filtering doesn't support filtering by table attribute names (only by field ID's)
    // https://community.baserow.io/t/filter-does-not-work/96
"""

Alokacija_Mappings = {
    "JMBAG": "field_1255530",
    "Student": "field_1255615",  # []
    "Alocirani_zadatak": "field_1255531",
    "popunjena_prijavnica": "field_1255532",
    "status_zahtjeva": "field_1255564",
    "datum_prijave": "field_1255617",
    "odustao": "field_1255618",
    "process_instance_id": "field_1290411",
    "frontend_url": "field_1290412",
    "predan_dnevnik_prakse": "field_1290864",
}

Student_Mappings = {
    "JMBAG": "field_1255533",
    "ime": "field_1255534",
    "prezime": "field_1268623",
    "email": "field_1269574",
    "godina_studija": "field_1255549",  # 1_prijediplomski, 2_prijediplomski, 3_prijediplomski, 1_diplomski, 2_diplomski
    "Student_preferencije": "field_1255583",  # []
    "Prijavnica": "field_1255589",
    "Dnevnik_prakse": "field_1255600",
    "Alokacija": "field_1255616",
}

Poslodavac_Mappings = {"naziv": "field_1255536", "web": "field_1255565"}

Zadaci_za_odabir_Mappings = {
    "id_zadatak": "field_1255543",
    "poslodavac_email": "field_1255544",
    "preferirane_tehnologije": "field_1255550",
    "preferencije_za_studenta": "field_1255551",
    "potrebno_imati": "field_1255552",
    "trajanje_sati": "field_1255553",
    "zeljeno_okvirno_vrijeme_pocetka": "field_1255554",
    "angazman_fipu": "field_1255555",
    "napomena": "field_1255556",
    "opis_zadatka": "field_1255557",
    "selekcija": "field_1255576",
    "proces_selekcije": "field_1255577",
    "Poslodavac": "field_1270742",
}
Student_preferencije_Mappings = {
    "JMBAG": "field_1255546",
    "Prvi_odabir": "field_1255547",
    "Drugi_odabir": "field_1255580",
    "Treci_odabir": "field_1255581",
    "Student": "field_1255582",  # []
    "napomena": "field_1255584",
}
Prijavnica_Mappings = {
    "OIB": "field_1255558",
    "Student": "field_1255588",
    "student_broj_mobitela": "field_1255590",
    "mentor_ime_prezime": "field_1255593",
    "opis_zadatka": "field_1255594",
    "datum_pocetka": "field_1255595",
    "datum_zavrsetka": "field_1255596",
    "alokacija_potvrđena": "field_1255597",
    "kontaktiranje_tvrtke_potvrđeno": "field_1255598",
    "student_email": "field_1255599",
    "Poslodavac": "field_1268742",
}
Dnevnik_prakse_Mappings = {
    "ID": "field_1255561",
    "Student": "field_1255562",
    "dnevnik_prakse_upload": "field_1255563",
    "pdf_ispunjene_potvrde_o_praksi": "field_1255601",
    "nastavak_rada": "field_1255602",
    "studomat_prijavljen_rok": "field_1255603",
}
