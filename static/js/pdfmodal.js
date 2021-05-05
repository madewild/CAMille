$(function () {
    var url_string = window.location.href;
    var url = new URL(url_string);
    var docid = url.searchParams.get("doc");
    var docurl = '/static/temp/' + docid + '.pdf';

    if(typeof(docid) != "undefined" && docid !== null) {
        var h = $(window).height();
        var object = "<object data='" + docurl + "' type='application/pdf' width='100%' height='99%'></object>";
        $("#pdfmodal").html(object);
        $("#pdfmodal").dialog({
            modal: true,
            title: docid,
            width: "50%",
            height: h
        });
    };
});

$(document).keydown(function(event) { 
    if (event.keyCode == 27) { 
      $('#pdfmodal').hide();
    }
  });
