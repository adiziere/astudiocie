// Galerie produit : clic sur une vignette -> image principale
document.querySelectorAll(".thumbs button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const main = document.getElementById("main-img");
    main.src = btn.dataset.src;
    main.alt = btn.dataset.alt;
    document.querySelectorAll(".thumbs button").forEach((b) => b.removeAttribute("aria-current"));
    btn.setAttribute("aria-current", "true");
  });
});

// Compte à rebours jusqu'au prochain produit
document.querySelectorAll("[data-countdown]").forEach((el) => {
  const target = new Date(el.dataset.countdown + "T00:00:00");
  const days = Math.ceil((target - new Date()) / 86400000);
  if (days > 1) el.textContent = "J-" + days;
  else if (days === 1) el.textContent = "Demain";
  else el.textContent = "Bientôt";
});
