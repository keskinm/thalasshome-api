

function validate() {
    var value = document.getElementById("choix_locations").value;
    console.log('jedebug!')
    console.log(value);

    $.ajax({  
        type : 'POST',
        crossDomain: true,
        // url : "{{url_for('trying')}}",
        // url : "https://locations-ecommerce.ew.r.appspot.com:8080/posting_scripts/trying",
        url : "https://locations-ecommerce.ew.r.appspot.com/trying",
        data : {"data": JSON.stringify(value)}, 
        success:function(result){
            console.log(result);
    
                  }
      });
  
      
}


