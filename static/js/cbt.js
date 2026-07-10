// Auro CBT page — clicking a library card selects it in the form dropdown
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".cbt-card");
  const select = document.getElementById("exercise_type");

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      cards.forEach((c) => c.classList.remove("active"));
      card.classList.add("active");
      if (select) {
        select.value = card.dataset.type;
      }
      document.querySelector('textarea[name="situation"]').focus();
    });
  });
});
