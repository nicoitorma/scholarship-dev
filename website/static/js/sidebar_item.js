$(document).ready(function () {
    // Get the current URL path
    var path = window.location.pathname;

    // Highlight the active item based on the path
    $(".nav-item").removeClass("active");
    $('.nav-item a[href="' + path + '"]')
      .parent()
      .addClass("active");
  });