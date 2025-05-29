document.addEventListener("DOMContentLoaded", () => {
  fetch('/static/data/news.json')
    .then(res => res.json())
    .then(news => {
      const container = document.getElementById("news-container");

      news.forEach(item => {
        container.innerHTML += `
          <div class="col-md-6 col-lg-4">
            <div class="card h-100 shadow-sm">
              ${item.images[0] ? `<img src="${item.images[0]}" class="card-img-top" alt="...">` : ""}
              <div class="card-body">
                <h5 class="card-title">${item.title}</h5>
                <h6 class="card-subtitle mb-2 text-muted">${item.date}</h6>
                <p class="card-text">${item.content}</p>
              </div>
            </div>
          </div>
        `;
      });
    })
    .catch(err => {
      console.error("Помилка при завантаженні новин:", err);
    });
});
