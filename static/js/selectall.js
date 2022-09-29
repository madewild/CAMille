$(document).ready(function () {
    $('body').on('click', '#selectAll', function () {
      if ($(this).hasClass('allChecked')) {
          $('input[type="checkbox"]', '#selectall').prop('checked', false);
      } else {
          $('input[type="checkbox"]', '#selectall').prop('checked', true);
      }
      $(this).toggleClass('allChecked');
    })
  });