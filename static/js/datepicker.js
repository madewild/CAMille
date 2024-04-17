$.datepicker.setDefaults($.datepicker.regional['fr']);
$( function() {
    var dateFormat = "yy-mm-dd",
      from = $("#date_from").datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        yearRange: "1831:1993",
        defaultDate: "1831-02-06"
      })
      .on( "change", function() {
        to.datepicker( "option", "minDate", getDate( this ) );
      }),
      to = $("#date_to").datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        yearRange: "1831:1993",
        defaultDate: "1993-09-01"
      })
      .on( "change", function() {
        from.datepicker( "option", "maxDate", getDate( this ) );
      });
 
    function getDate( element ) {
      var date;
      try {
        date = $.datepicker.parseDate( dateFormat, element.value );
      } catch( error ) {
        date = null;
      }
 
      return date;
    }
  } );