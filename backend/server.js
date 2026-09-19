const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve the actual website
app.use(express.static(path.join(__dirname, "..", "frontend")));

// Health check — useful when we connect the frontend to the real backend
app.get("/api/health", (req, res) => {
  res.json({
    success: true,
    service: "ChainVault API",
    status: "running",
    project: "Blockchain-Based Secure Platform for Identity, Access Control, and Digital Asset Management"
  });
});

// Home page
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "frontend", "index.html"));
});

// Temporary routes so the navbar works.
// These will become real authentication pages when we build login/register.
app.get("/login", (req, res) => {
  res.status(501).send("Login page will be implemented in the authentication module.");
});

app.get("/register", (req, res) => {
  res.status(501).send("Registration page will be implemented in the authentication module.");
});

// 404 API response
app.use("/api", (req, res) => {
  res.status(404).json({ success: false, message: "API endpoint not found" });
});

app.listen(PORT, () => {
  console.log(`ChainVault running at http://localhost:${PORT}`);
});
