$(document).ready(function () {
  $('.modal').on('hidden.bs.modal', function (e) {
    $("#update-article-form").trigger("reset");
    $('#category-select').empty();
    $('#category-list').empty();
    $('#category-select').append('<option value="" disabled selected>Select a category</option>');
  });
});

function showArticle(card) {
  const articleId = card.dataset.id;
  const article = $("#article-modal");
  fetch(`/article/${articleId}`)
    .then(response => response.json())
    .then(data => {
      article.find("#article-modal-title").text(data.title);
      article.find("#article-modal-lead").text(data.lead_paragraph);
      article.find("#article-modal-category").text(data.category);
      article.find("#article-modal-content").text(data.content);
    });
  article.modal('show');
}

function deleteArticle(button) {
  const articleId = button.dataset.articleId;
  fetch(`/article/${articleId}`, { method: 'DELETE' })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        location.reload();
      }
    });
}

function getCategories(id) {
  const categories = $("#category-select");
  fetch("/categories")
    .then(response => response.json())
    .then(data => {
      data.forEach(category => {
        if (id && id === category._id) {
          categories.append(`<option value="${category._id}" selected>${category.category}</option>`);
          return;
        }
        categories.append(`<option value="${category._id}">${category.category}</option>`);
      });
    });
}

function openDeleteModal(articleId) {
  const deleteModal = $("#delete-modal");
  deleteModal.find("#delete-modal-button").attr("data-article-id", articleId);
  deleteModal.modal('show');
}

function openAddModal() {
  const articleModal = $("#add-modal");
  getCategories(null);
  articleModal.modal('show');
}

function openEditModal(articleId) {
  const articleModal = $("#add-modal");
  articleModal.find("#update-article-form").attr("action", `/article/${articleId}`);
  articleModal.find(".modal-title").text("Edit Article");
  articleModal.find('button[type="submit"]').text("Update");
  const articleForm = $("#update-article-form");
  fetch(`/article/${articleId}`)
    .then(response => response.json())
    .then(data => {
      articleForm.find("#title").val(data.title);
      articleForm.find("#lead-paragraph").val(data.lead_paragraph);
      articleForm.find("#category-select").val(data.category_id);
      articleForm.find("#content").val(data.content);
      getCategories(data.category_id);
    });
  articleModal.modal('show');
}

function openMenu(checkbox) {
  if (checkbox.checked) {
    $('#left-menu').fadeIn(200);
    $('<div id="menu-overlay"></div>')
      .hide()
      .appendTo('body')
      .fadeIn('fast');
    $('body').addClass('menu-open');
  } else {
    $('#left-menu').fadeOut(200);
    $('#menu-overlay').fadeOut('fast', function () {
      $(this).remove();
    });
    $('body').removeClass('menu-open');
  }
}

function categoriesList() {
  fetch("/categories")
    .then(response => response.json())
    .then(data => {
      const categories = $("#category-list");
      data.forEach(category => {
        categories.append(`<li class="list-group-item d-flex justify-content-between"><p class="h6">${category.category}<p>
        <div class="d-flex justify-content-between gap-3">
        <i class="bi bi-pencil-fill" style="color:black;" onclick="updateCategory('`+ category._id + `')"></i>
        <i class="bi bi-trash3-fill" style="color:red;" onclick="deleteCategory('`+ category._id + `')"></i>
        </div>
        </li>`);
      });
    });
}

function openCategoryModal() {
  categoriesList();
  $("#categoryModal").modal('show');

}

function deleteCategory(categoryId) {
  console.log(categoryId);
  fetch('/category/' + categoryId, { method: 'DELETE' })
    .then(response => {
      if (response.ok) {
        location.reload();
      }
      else if (response.status === 400) {
        $('#category-error').append(`<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>Oops!</strong> Cannot delete the category while articles are still associated with it.<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`);
      }
    });

}


function updateCategory(categoryId) {

}

function downloadArticle(articleId) {
  fetch(`/article/${articleId}`, { method: 'GET' })
    .then(response => response.json())
    .then(data => {
      const article = {
        title: data.title,
        lead_paragraph: data.lead_paragraph,
        category: data.category,
        content: data.content
      };
      const article_title = article.title.replace(/ /g, "_").toLowerCase();
      const csvData = Object.keys(article).map(key => `"${article[key]}"`).join(',');
      const csv = Object.keys(article).join(',') + '\n' + csvData;
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.setAttribute('hidden', '');
      a.setAttribute('href', url);
      a.setAttribute('download', article_title + `.csv`);
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });
}



document.addEventListener('DOMContentLoaded', function () {
  fetch('/chartdata')
    .then(response => response.json())
    .then(data => {
      const ctx = document.getElementById('myChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(item => item.category),
          datasets: [{
            label: 'Articles per category',
            data: data.map(item => item.count),
            borderWidth: 1
          }]
        },
        options: {
          scale: {
            ticks: {
              precision: 0,
            }
          }
        }
      });
    });
});

