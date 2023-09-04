import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import "dotenv/config";
import pdf from "./pdf.js";

const app = express();
const DEFAULT_PORT = 3001;
const port = process.env.PORT || DEFAULT_PORT;
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Middleware Setup
app.use(cors());
app.use(bodyParser.json({ limit: "5mb" }));
app.use(
  bodyParser.urlencoded({
    limit: "5mb",
    extended: true,
    parameterLimit: 5000,
  })
);
app.use(express.json());
app.set("view engine", "ejs");

// API Routes
app.get("/api/status", (req, res) => {
  res.status(200).json({
    microservice: "pdf-maker-service-node",
    status: "OK",
    message: "Service is running",
    status_check_timestamp: new Date().toISOString(),
  });
});

app.use("/api", pdf);
app.use("/api/potvrda", express.static(path.join(__dirname, "potvrde")));

// Start the server
app.listen(port, () => {
  console.log(`Listening on port ${port} ✅`);
});
