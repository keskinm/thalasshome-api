
function makeSortable(id, socket) {

    const el = document.getElementById(id);
    const sortable = Sortable.create(el, {
        animation: 150,
        group: 'lists',
        onAdd: function (ev) {
            const cld = ev.item.childNodes;
            let item_id = undefined;

            for (let i = 0; i < cld.length; i++) {
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

const cat = ['ask', 'delivery', 'client', 'stock', 'done', 'canceled'];


const socket = io.connect('http://127.0.0.1:8080/');
socket.on('update', function(msg) {

    const it = msg;

    for (let i = 0; i < cat.length; i++) {
        const i_list = it[cat[i]];
        const cont = document.getElementById(cat[i]);

        /*while (cont.firstChild)
            cont.removeChild(cont.lastChild);*/

        if (i_list === undefined) {
            cont.innerHTML = "";
            continue;
        }

        let new_content = "";

        for (let j = 0; j < i_list.length; j++) {
            const cur_item = i_list[j];

            new_content += `<li>\
                ${ cur_item.address } <br />\
                Employé: ${ cur_item.def_empl } <br />\
                Remplacant: ${ cur_item.rep_empl } <br />\
                Objets: ${ cur_item.shipped }\
                <p hidden>${ cur_item.ent_id }</p>\
            </li>`
        }

        cont.innerHTML = new_content;
    }

});

function selectOnly(zone) {
    socket.emit('ask_zone', {
        zone: zone
    })
}

$(function (){

    for (let i = 0; i < cat.length; i++)
        makeSortable(cat[i], socket);

});
