import { Router } from "express";
import { chromium } from "playwright";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import crypto from "crypto";
import "dotenv/config";

const router = Router();

// Constants
const PDF_MIME_TYPE = "data:application/pdf;base64";

// Utility functions
function replacePlaceholders(template, data) {
  for (const key in data) {
    const placeholder = `$${key}`;
    const value = data[key];
    template = template.replace(placeholder, value);
  }
  return template;
}

function generateHash(oib, mobile) {
  const shasum = crypto.createHash("sha1");
  shasum.update(oib + mobile);
  return shasum.digest("hex");
}

async function generatePDFContent(page, jsonData) {
  const htmlTemplate = await fs.readFile("index.html", "utf8");
  const htmlContent = replacePlaceholders(htmlTemplate, jsonData);
  await page.setContent(htmlContent);
}

async function applyStyles(page) {
  await page.addStyleTag({ content: "@page { margin: 0cm; }" });
  await page.addStyleTag({ path: "css/katex.min.css" });
  await page.addStyleTag({ path: "css/qcss.css" });
  await page.addStyleTag({ path: "css/tailwind.css" });
  await page.addStyleTag({
    content:
      "* {print-color-adjust: exact; -webkit-print-color-adjust: exact;}",
  });
}

router.post("/potvrda", async (req, res) => {
  try {
    const jsonData = req.body;

    const browser = await chromium.launch({
      args: [
        "--no-sandbox",
        "--headless",
        "--hide-scrollbars",
        "--printBackground=true",
        "--disable-dev-shm-usage",
        "--font-render-hinting=medium",
      ],
    });

    const page = await browser.newPage();
    await generatePDFContent(page, jsonData);
    await applyStyles(page);

    await page.evaluate(() => matchMedia("screen").matches);
    await page.emulateMedia({ media: "screen" });

    const pdfBuffer = await page.pdf({ format: "A4" });
    await browser.close();

    const fileName =
      generateHash(jsonData.student_OIB, jsonData.student_broj_mobitela) +
      ".pdf";

    const currentModulePath = fileURLToPath(import.meta.url);
    const currentModuleDir = path.dirname(currentModulePath);
    const filePath = path.join(currentModuleDir, "potvrde", fileName);
    await fs.writeFile(filePath, pdfBuffer);

    res.json({
      pdf_attachment_url: `${process.env.SERVICE_URL}:${process.env.PORT}/api/potvrda/${fileName}`,
    });
  } catch (error) {
    console.error(error);
    res.status(500).send("Internal Server Error");
  }
});

export default router;
