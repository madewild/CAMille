var minValueDay = getParameterByName('day_from') || 1;
var maxValueDay = getParameterByName('day_to') || 31;

$( function() {
  $("#slider-range-day").slider({
    range: true,
    min: 1,
    max: 31,
    values: [minValueDay, maxValueDay],
    slide: function( event, ui ) {
      $('#day_range').val("Du " + ui.values[0] + " au " + ui.values[1]);
      if (ui.values[0] < 10) {
        $df = "0" + ui.values[0];
      } else {
        $df = ui.values[0];
      }
      $('#day_from').val($df);
      if (ui.values[1] < 10) {
        $dt = "0" + ui.values[1];
      } else {
        $dt = ui.values[1];
      }
      $('#day_to').val($dt);
    }
  });
  $("#day_range").val("Du " + $("#slider-range-day").slider("values", 0) +
    " au " + $("#slider-range-day").slider("values", 1));
} );
