
function makeSortable(id) {

    var el = document.getElementById(id);
    var sortable = Sortable.create(el, {
        animation: 150,
        group: 'lists'
    });

}

$(function (){

    makeSortable("ask");
    makeSortable("in_progress");
    makeSortable("done");
    makeSortable("canceled");

});
