import unittest
from unittest import IsolatedAsyncioTestCase
import main as m
import asyncio

"""
class Request:
    pass


class RequestPdf(Request):
    query = {"to": "nikola.tankovic@gmail.com"}

    query_string = "OK"

    async def json(self):
        return {
            "next_task": "evaluacija_poslodavac",
            "attachment_url": "http://localhost:8083/public/a2ef93dc729c2335c8955faa30c651e39408.pdf",
            "id_instance": "c392f6e3-ee73-4ae2-b0c8-d76f24baf03d",
            "_frontend_url": "http://localhost:9000",
        }


class RequestApproval(Request):
    query = {"to": "nikola.tankovic@gmail.com"}

    query_string = "OK"

    async def json(self):
        return {
            "next_task": "evaluacija_poslodavac",
            "email_student": "nikola.tankovic@gmail.com",
            "ime_student": "Nikola Tanković",
            "godina_studija": "1. diplomski",
            "id_instance": "c392f6e3-ee73-4ae2-b0c8-d76f24baf03d",
            "_frontend_url": "http://localhost:9000",
        }


class Test(IsolatedAsyncioTestCase):
    async def test_request_approval(self):
        r = RequestApproval()
        result = await m.send_email_poslodavac_after_allocation(r)
        self.assertEqual(1, 1)

    async def test_pdf(self):
        r = RequestPdf()
        result = await m.send_email_student_pdf(r)
        self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main()
"""
