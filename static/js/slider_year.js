var minValueYear = getParameterByName('year_from') || 1831;
var maxValueYear = getParameterByName('year_to') || 1970;

$( function() {
  $("#slider-range-year").slider({
    range: true,
    min: 1831,
    max: 1970,
    values: [minValueYear, maxValueYear],
    slide: function(event, ui) {
      $('#year_range').val("De " + ui.values[0] + " à " + ui.values[1]);
      $('#year_from').val(ui.values[0]);
      $('#year_to').val(ui.values[1]);
    }
  });
  $("#year_range").val("De " + $("#slider-range-year").slider("values", 0) +
    " à " + $("#slider-range-year").slider("values", 1));
} );

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
      results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
  }