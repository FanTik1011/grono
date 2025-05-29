document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/news")
    .then(res => res.json())
    .then(data => renderNews(data));
});

function renderNews(news) {
  const container = document.getElementById("news-container");
  container.innerHTML = "";

  // Сортуємо за датою або id (якщо нема ISO-дат)
  const sorted = news.sort((a, b) => b.id - a.id); // або за датою, якщо вона ISO

  // Беремо тільки 3 останніх
  const latestNews = sorted.slice(0, 3);

  latestNews.forEach(item => {
    const col = document.createElement("div");
    col.className = "col-md-6 col-lg-4";

    col.innerHTML = `
      <div class="card h-100 glass-card" data-aos="fade-up">
        <img src="${item.images[0] || '/static/images/default.jpg'}" class="card-img-top" alt="${item.title}">
        <div class="card-body">
          <h5 class="card-title">${item.title}</h5>
          <p class="card-text">${item.content}</p>
        </div>
        <div class="card-footer text-muted">
          ${item.date}
        </div>
      </div>
    `;

    container.appendChild(col);
  });
}
