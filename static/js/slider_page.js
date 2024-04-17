var minValuePage = getParameterByName('page_from') || 1;
var maxValuePage = getParameterByName('page_to') || 516;

$( function() {
  $("#slider-range-page").slider({
    range: true,
    min: 1,
    max: 516,
    values: [minValuePage, maxValuePage],
    slide: function( event, ui ) {
      $('#page_range').val("De la page " + ui.values[0] + " à la page " + ui.values[1]);
      if (ui.values[0] < 10) {
        $pf = "0000" + ui.values[0];
      } else if (ui.values[0] < 100) {
        $pf = "000" + ui.values[0];
      } else {
        $pf = "00" + ui.values[0];
      }
      $('#page_from').val($pf);
      if (ui.values[1] < 10) {
        $pt = "0000" + ui.values[1];
      } else if (ui.values[0] < 100) {
        $pf = "000" + ui.values[0];
      } else {
        $pf = "00" + ui.values[0];
      }
      $('#page_to').val($pt);
    }
  });
  $("#page_range").val("De la page " + $("#slider-range-page").slider("values", 0) +
    " à la page " + $("#slider-range-page").slider("values", 1));
} );
