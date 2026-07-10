// Auro dashboard interactivity — live slider readouts
document.addEventListener("DOMContentLoaded", () => {
  const pairs = [
    ["mood_score", "mood_score_val"],
    ["anxiety_score", "anxiety_score_val"],
  ];
  pairs.forEach(([inputId, labelId]) => {
    const input = document.getElementById(inputId);
    const label = document.getElementById(labelId);
    if (!input || !label) return;
    input.addEventListener("input", () => {
      label.textContent = input.value;
    });
  });
});
