"""
    // normal fields are in lower_case
    // table references fields are in Upper_case
    // Exception: JMBAG, OIB, ID
    
    // Why all this? Because baserow filtering doesn't support filtering by table attribute names (only by field ID's)
    // https://community.baserow.io/t/filter-does-not-work/96
"""

Alokacija_Mappings = {
    "id_alokacija": "field_4523",
    "Student_preferencije": "field_4619",
    "JMBAG": "field_4570",
    "Student": "field_4539",  # []
    "Alocirani_zadatak": "field_4621",
    "popunjena_prijavnica": "field_4577",
    "status_zahtjeva": "field_4576",  # evaluacija_u_tijeku - 2457, student_prihvaćen - 2458, student_odbijen - 2459, student_odustao - 2460, profesor_ponistio - 2461
    "datum_prijave": "field_4573",
    "odustao": "field_1255618",
    "process_instance_id": "field_4571",
    "frontend_url": "field_4572",
    "predan_dnevnik_prakse": "field_4578",
}

Student_Mappings = {
    "JMBAG": "field_4510",
    "ime": "field_4511",
    "prezime": "field_4512",
    "avatar": "field_4533",  # File
    "email": "field_4513",
    "godina_studija": "field_4532",  # 1_prijediplomski, 2_prijediplomski, 3_prijediplomski, 1_diplomski, 2_diplomski
    "Student_preferencije": "field_4534",  # []
    "Prijavnica": "field_4536",
    "Dnevnik_prakse": "field_4611",
    "Alokacija": "field_4538",
    "Model_prakse": "field_4639",
    "process_instance_id": "field_4640"
}

Poslodavac_Mappings = {
    "naziv": "field_4514",
    "web": "field_4515",
    "direktor": "field_4516",
    "maticni_broj": "field_4540",
    "OIB": "field_4541",
    "adresa": "field_4542",
    "logo": "field_4543",
}

Zadaci_za_odabir_Mappings = {
    "id_zadatak": "field_4517",
    "voditelj_odobrio": "field_4518",
    "Poslodavac": "field_4623",
    "poslodavac_email": "field_4546",
    "broj_studenata": "field_4547",
    "dostupno_mjesta": "field_4585",
    "preferirane_tehnologije": "field_4549",
    "preferencije_za_studenta": "field_4552",
    "potrebno_imati": "field_4550",
    "trajanje_sati": "field_4551",
    "zeljeno_okvirno_vrijeme_pocetka": "field_4554",
    "angazman_fipu": "field_4555",
    "napomena": "field_4556",
    "opis_zadatka": "field_4548",
    "selekcija": "field_4557",
    "proces_selekcije": "field_4558",
    "Poslodavac": "field_1270742",
    "total_alokacija": "field_4583",
    "statusi_alokacija": "field_4584",
    "lokacija": "field_4553",
}
Student_preferencije_Mappings = {
    "id_preferencije": "field_4520",
    "JMBAG": "field_4521",
    "Prvi_odabir": "field_4586",
    "Drugi_odabir": "field_4587",
    "Treci_odabir": "field_4588",
    "Student": "field_4535",  # []
    "napomena": "field_4567",
    "Alokacija": "field_4620",
}
Prijavnica_Mappings = {
    "id_prijavnica": "field_4526",
    "Alokacija": "field_4580",
    "pdf_attachment_url": "field_4607",  # url
    "Student": "field_4537",
    "process_instance_id": "field_4591",
    "student_broj_mobitela": "field_4592",
    "student_email": "field_4594",
    "detaljan_opis_zadatka": "field_4598",
    "pocetak_prakse": "field_4600",
    "kraj_prakse": "field_4601",
    "alokacija_potvrda": "field_4602",
    "kontakt_potvrda": "field_4603",
    "mentor_ime": "field_4595",
    "mentor_prezime": "field_4596",
    "mjesto_izvrsavanja": "field_4606",
    "mentor_email": "field_4597",
    "student_OIB": "field_4593",
    "dogovoreni_broj_sati": "field_4599",
}
Dnevnik_prakse_Mappings = {
    "id_dnevnik_prakse": "field_4529",
    "Alokacija": "field_4582",
    "Student": "field_4610",
    "process_instance_id": "field_4614",
    "id_prijavnica": "field_4612",
    "dnevnik_prakse_upload": "field_4615",
    "ispunjena_potvrda_upload": "field_4616",
    "nastavak_radnog_odnosa": "field_4617",
    "prijavljen_rok": "field_4618",
    "Prijavnica": "field_4609",
}
