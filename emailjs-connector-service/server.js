import "dotenv/config";
import express from "express";
import fs from "fs";
import path from "path";
import handlebars from "handlebars";
import axios from "axios";
import { fileURLToPath } from "url";
import cors from "cors";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json());

const allowedTemplates = [
  "mentor_potvrda_pdf",
  "poslodavac_after_allocation",
  "student_after_allocation",
  "student_after_approval",
  "student_after_refusal",
  "student_after_return",
  "student_potvrda_pdf",
  "model_b_student_odobren_zadatak",
];

// Map for titles
const titleMap = {
  poslodavac_after_allocation: "FIPU Praksa: Potvrda o Alokaciji",
  student_after_allocation: "FIPU Praksa: Potvrda o Alokaciji",
  student_after_approval: "FIPU Praksa: Student prihvaćen",
  student_potvrda_pdf: "FIPU Praksa: Potvrda o praksi",
  mentor_potvrda_pdf: "FIPU Praksa: Potvrda o praksi",
  student_after_refusal: "FIPU Praksa: Student odbijen",
  student_after_return: "FIPU Praksa: Odabir poništen",
  model_b_student_odobren_zadatak: "FIPU Praksa: Zadatak odobren",
};

const serviceId = process.env.SERVICE_ID;
const templateId = process.env.TEMPLATE_ID;
const publicKey = process.env.PUBLIC_KEY;
const privateKey = process.env.PRIVATE_KEY;

app.post("/email", (req, res) => {
  const templateName = req.query.template;
  const toEmail = req.query.to; // Recipient's email address from query parameter

  if (!templateName) {
    return res.status(400).send("Template query parameter is required.");
  }

  if (!allowedTemplates.includes(templateName)) {
    return res.status(400).send("Invalid template name.");
  }

  if (!toEmail) {
    return res
      .status(400)
      .send("Recipient email (to) is required in the query parameters.");
  }

  const templatePath = path.join(
    __dirname,
    "templates",
    `${templateName}.html`
  );

  fs.readFile(templatePath, "utf8", (err, templateContent) => {
    if (err) {
      console.error(err);
      return res.status(500).send("Error reading template file.");
    }

    const template = handlebars.compile(templateContent);

    const htmlContent = template(req.body);

    const emailTitle = titleMap[templateName] || "FIPU Praksa";

    const templateParams = {
      message: htmlContent,
      to_email: toEmail,
      title: emailTitle,
      // Include any additional parameters required by your EmailJS template
    };

    // Send the email using EmailJS
    axios
      .post(
        "https://api.emailjs.com/api/v1.0/email/send",
        {
          service_id: serviceId,
          template_id: templateId,
          user_id: publicKey,
          accessToken: privateKey,
          template_params: templateParams,
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${privateKey}`,
          },
        }
      )
      .then((response) => {
        console.log("Email sent successfully:", response.data);
        res.send("Email sent successfully.");
      })
      .catch((error) => {
        console.error(
          "Error sending email:",
          error.response ? error.response.data : error.message
        );
        res.status(500).send("Error sending email.");
      });
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
