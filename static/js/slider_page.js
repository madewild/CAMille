var minValuePage = getParameterByName('page_from') || 1;
var maxValuePage = getParameterByName('page_to') || 70;

$( function() {
  $("#slider-range-page").slider({
    range: true,
    min: 1,
    max: 70,
    values: [minValuePage, maxValuePage],
    slide: function( event, ui ) {
      $('#page_range').val("De la page " + ui.values[0] + " à la page " + ui.values[1]);
      if (ui.values[0] < 10) {
        $pf = "0000" + ui.values[0];
      } else {
        $pf = "000" + ui.values[0];
      }
      $('#page_from').val($pf);
      if (ui.values[1] < 10) {
        $pt = "0000" + ui.values[1];
      } else {
        $pt = "000" + ui.values[1];
      }
      $('#page_to').val($pt);
    }
  });
  $("#page_range").val("De la page " + $("#slider-range-page").slider("values", 0) +
    " à la page " + $("#slider-range-page").slider("values", 1));
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