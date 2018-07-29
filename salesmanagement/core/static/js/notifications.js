$(document).ready(function(){
    $('#notifications button').click(function(){
        var li = $(this).parent('li');
        var url = $(this).data('remove-url');
        $.get(url).fail(function() {
            alert("Ocorreu algum erro, contate o administrador");
        }).always(function() {
            li.hide(100);
        });
    })
});