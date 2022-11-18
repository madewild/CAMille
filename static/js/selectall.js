$(document).ready(function () {
    $('body').on('click', '#selectAllPapers', function () {
      if ($(this).hasClass('allChecked')) {
          $('input[type="checkbox"]', '#selectallpapers').prop('checked', false);
      } else {
          $('input[type="checkbox"]', '#selectallpapers').prop('checked', true);
      }
      $(this).toggleClass('allChecked');
    })
  });
$(document).ready(function () {
    $('body').on('click', '#selectAllMonths', function () {
      if ($(this).hasClass('allChecked')) {
          $('input[type="checkbox"]', '#selectallmonths').prop('checked', false);
      } else {
          $('input[type="checkbox"]', '#selectallmonths').prop('checked', true);
      }
      $(this).toggleClass('allChecked');
    })
  });
$(document).ready(function () {
    $('body').on('click', '#selectAllDays', function () {
      if ($(this).hasClass('allChecked')) {
          $('input[type="checkbox"]', '#selectalldays').prop('checked', false);
      } else {
          $('input[type="checkbox"]', '#selectalldays').prop('checked', true);
      }
      $(this).toggleClass('allChecked');
    })
  });