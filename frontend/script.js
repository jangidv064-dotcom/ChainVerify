const menuBtn = document.getElementById("menuBtn");
const navLinks = document.querySelector(".nav-links");

menuBtn?.addEventListener("click", () => {
  const open = navLinks.style.display === "flex";
  navLinks.style.display = open ? "" : "flex";
  navLinks.style.position = "absolute";
  navLinks.style.top = "76px";
  navLinks.style.left = "0";
  navLinks.style.right = "0";
  navLinks.style.padding = "18px 7%";
  navLinks.style.background = "#fff";
  navLinks.style.flexDirection = "column";
  navLinks.style.borderBottom = "1px solid #e9eef5";
});

async function checkBackend() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error();
    console.log("ChainVault backend connected.");
  } catch {
    console.log("Backend is not running.");
  }
}

checkBackend();
