var minValue = getParameterByName('year_from') || 1831;
var maxValue = getParameterByName('year_to') || 1970;

$( function() {
  $( "#slider-range" ).slider({
    range: true,
    min: 1831,
    max: 1970,
    values: [ minValue, maxValue ],
    slide: function( event, ui ) {
      $( "#amount" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
      $('#year_from').val(ui.values[ 0 ]);
      $('#year_to').val(ui.values[ 1 ]);
    }
  });
  $( "#amount" ).val($( "#slider-range" ).slider( "values", 0 ) +
    " - " + $( "#slider-range" ).slider( "values", 1 ) );
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