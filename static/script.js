
function makeSortable(id, socket) {

    var el = document.getElementById(id);
    var sortable = Sortable.create(el, {
        animation: 150,
        group: 'lists',
        onAdd: function (ev) {
            var cld = ev.item.childNodes;
            var item_id = undefined;

            for (var i = 0; i < cld.length; i++) {
                if (cld[i].localName === "p") {
                    item_id = cld[i].textContent;
                    break;
                }
            }

            socket.emit('category', {
                item: item_id,
                category: ev.to.id
            });
        }
    });

}

$(function (){

    var socket = io.connect('http://' + document.domain + ':8000/');

    socket.on('endpoint', function(msg) {
        alert('Received: ' + msg.data);
    });
    /*$('form').submit(function(event) {
        socket.emit('add_to_queue', {data: $('#data').val()});
        return false;
    });*/

    makeSortable("ask", socket);
    makeSortable("delivery", socket);
    makeSortable("client", socket);
    makeSortable("stock", socket);
    makeSortable("done", socket);
    makeSortable("canceled", socket);

});
