// ----------------------------------- GLOBAL VARS -----------------------------------------------


const cat = ['ask', 'assigned', 'in_delivery', 'delivered', 'canceled'];



// ----------------------------------- EVENT FUNCTIONS -----------------------------------------------


function select_repl(select, item_id) {
    let substitute = undefined;

    for (let i = 0; i < select.length; i++) {
      if (select[i].selected) {
        substitute = select[i].label;
        break;
      }
    }

    fetch('/select_repl', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        substitute: substitute,
        item_id: item_id
      })
    })
      .then(response => response.json())
      .then(data => {
        console.log("Replacement updated:", data);
        // data.message, data.item_id, data.replace ...
        // Si besoin, tu peux faire un refresh sur l'écran,
        // ou juste afficher une petite notification
      })
      .catch(error => {
        console.error('Error updating replacement:', error);
      });
}


function removeCards(list_id) {
    fetch('/remove_cards', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ list_id })
    })
      .then(response => response.json())
      .then(data => {
        console.log("Removed cards:", data);
        const cont = document.getElementById(data.list_id);
        if (cont) {
          cont.innerHTML = "";
        }

      })
      .catch(error => {
        console.error('Error removing cards:', error);
      });
  }





function selectOnly(zone, country) {
    fetch('/ask_zone', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ zone, country })
    })
      .then(response => response.json())
      .then(data => {
        for (let i = 0; i < cat.length; i++) {
          const i_list = data[cat[i]];
          const cont = document.getElementById(cat[i]);

          if (!i_list) {
            cont.innerHTML = "";
            continue;
          }

          let new_content = "";

          for (let j = 0; j < i_list.length; j++) {
            const cur_item = i_list[j];
            new_content += `
              <li>
                ${cur_item.address} <br />
                Employé: ${cur_item.def_empl} <br />
                Remplacant: ${cur_item.rep_empl} <br />
                Objets: ${cur_item.shipped} <br />
                Montant restant dû: ${cur_item.amount}€
                <p hidden>${cur_item.item_id}</p>
              </li>`;
          }

          cont.innerHTML = new_content;
        }
      })
      .catch(error => {
        console.error('Error fetching zone data:', error);
      });
  }
