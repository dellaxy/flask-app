$(document).ready(function () {
    const categories_menu = $('#categories-menu');
    fetch("/categories")
        .then(response => response.json())
        .then(data => {
            data.forEach(category => {
                const categoryLink = `<li><a class='dropdown-item' href='/category/${category._id}'>${category.category}</a></li>`;
                categories_menu.append(categoryLink);
            })
        });
});

function openArticle(articleId) {
    window.location.href = `/articles/${articleId}`;
}