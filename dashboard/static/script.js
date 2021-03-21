const cat = ['ask', 'delivery', 'client', 'stock', 'done', 'canceled'];

var ws_address = document.getElementsByName('ws_address')[0].content;
const socket = io.connect('ws://' + ws_address + '/');


function select_repl(select, item_id)
    {
     let select_label = undefined;

     for (let i = 0; i < select.length; i++) {
         if (select[i].selected === true) {
             select_label = select[i].label;
             break;
         }
    }

     socket.emit('select_repl', {
        select_label: select_label,
        item_id: item_id,
    });

    }

function removeCards(list_id) {
    {

    socket.emit('remove_cards', {
        list_id: list_id
    });
}
}

function makeSortable(id, socket) {

    const el = document.getElementById(id);
    const sortable = Sortable.create(el, {
        animation: 150,
        group: 'lists',
        onAdd: function (ev) {
            console.log('on_add', ev);
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
        },

        // onRemove: function (ev) {
        //     console.log('on_remove', ev);
        //     if (ev.to.id=='canceled') {
        //         console.log('in if statement', ev);
        //         const cld = ev.item.childNodes;
        //         let item_id = undefined;
        //
        //         for (let i = 0; i < cld.length; i++) {
        //             if (cld[i].localName === "p") {
        //                 item_id = cld[i].textContent;
        //                 break;
        //             }
        //         }
        //
        //         socket.emit('remove_card', {
        //             item: item_id,
        //             category: ev.to.id
        //     });
        //
        //     }
        // }

    });

}

function selectOnly(zone) {
    socket.emit('ask_zone', {
        zone: zone
    })
}

$(function (){

    for (let i = 0; i < cat.length; i++)
        makeSortable(cat[i], socket);

});


socket.on('ask_zone_client', function(msg) {

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
                Objets: ${ cur_item.shipped } \
                <p hidden>${ cur_item.ent_id }</p>\
            </li>`
        }

        cont.innerHTML = new_content;
    }

});