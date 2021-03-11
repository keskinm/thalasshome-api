
function makeSortable(id) {

    var el = document.getElementById(id);
    var sortable = Sortable.create(el, {
        animation: 150,
        group: 'lists'
    });

}

$(function (){

    makeSortable("ask");
    makeSortable("delivery");
    makeSortable("client");
    makeSortable("stock");
    makeSortable("done");
    makeSortable("canceled");

});
