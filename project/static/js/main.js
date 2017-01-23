
$('#sidebar-toggle').click(function() {
    var sidebar = $('#sidebar');
    var toggle = $('#sidebar-toggle');
    if (sidebar.is(":visible")) {
        $('#sidebar').hide();
        toggle.text('>');
    } else {
        $('#sidebar').show();
        toggle.text('X');
    }
});
