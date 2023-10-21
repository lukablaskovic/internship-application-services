import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import "dotenv/config";
import pdf from "./pdf.js";
import Bugsnag from "@bugsnag/js";
import bugsnagPluginExpress from "@bugsnag/plugin-express";

const app = express();
const DEFAULT_PORT = 3001;
const port = process.env.PORT || DEFAULT_PORT;
const __dirname = path.dirname(fileURLToPath(import.meta.url));

Bugsnag.start({
  apiKey: process.env.BUGSNAG,
  plugins: [bugsnagPluginExpress],
});

var middleware = Bugsnag.getPlugin("express");
app.use(middleware.requestHandler);
app.use(middleware.errorHandler);

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
app.get("/status", (req, res) => {
  res.status(200).json({
    microservice: "pdf-generator-connector-service",
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

// npx nodemon server.js
