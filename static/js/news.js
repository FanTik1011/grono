document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/news")
    .then(res => res.json())
    .then(data => renderNews(data))
    .catch(err => console.error("Помилка завантаження новин:", err));
});

function renderNews(news) {
  const container = document.getElementById("news-container");
  if (!container) {
    console.error("❌ #news-container не знайдено!");
    return;
  }

  container.innerHTML = "";

  const sorted = news
    .filter(n => n) // без null
    .sort((a, b) => (b.id || 0) - (a.id || 0));

  const latestNews = sorted.slice(0, 3);

  latestNews.forEach(item => {
    const col = document.createElement("div");
    col.className = "col-md-6 col-lg-4 mb-4";

    const img = item.images?.[0] || "/static/images/default.jpg";

    col.innerHTML = `
      <div class="card h-100 shadow-lg border-0 rounded-4 overflow-hidden glass-card" data-aos="fade-up">
        <img src="${img}" class="card-img-top" alt="${item.title || 'Новина'}">

        <div class="card-body">
          <h5 class="card-title fw-bold">${item.title || "Без назви"}</h5>
          <p class="card-text text-dark opacity-75">
              ${item.content || ""}
          </p>
        </div>

        <div class="card-footer bg-transparent text-muted small">
          ${item.date || ""}
        </div>
      </div>
    `;

    container.appendChild(col);
  });
}
