import "dotenv/config";
import express from "express";
import cors from "cors";
import { handleAnalyze } from "./routes/analyze";

export function createServer() {
  const app = express();

  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Example API routes
  app.get("/api/ping", (_req, res) => {
    const ping = process.env.PING_MESSAGE ?? "ping";
    res.json({ message: ping });
  });

  app.post("/api/analyze", handleAnalyze);



  return app;
}
