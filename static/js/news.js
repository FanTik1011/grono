fetch('data/news.json')
  .then(response => response.json())
  .then(data => {
    const newsContainer = document.getElementById('news-container');
    data.forEach(news => {
      const newsElement = document.createElement('div');
      newsElement.className = 'card mb-3';
      newsElement.innerHTML = `
        <div class="card-body">
          <h5 class="card-title">${news.title}</h5>
          <h6 class="card-subtitle mb-2 text-muted">${news.date}</h6>
          <p class="card-text">${news.content}</p>
        </div>
      `;
      newsContainer.appendChild(newsElement);
    });
  })
  .catch(error => {
    console.error('Помилка при завантаженні новин:', error);
  });