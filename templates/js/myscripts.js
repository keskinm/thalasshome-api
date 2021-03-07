

function validate() {
    var value = document.getElementById("choix_locations").value;
    console.log(value);

    $.ajax({  
        type : 'POST',
        crossDomain: true,
        url : "http://locations-ecommerce.ew.r.appspot.com/trying",
        data : {"data": JSON.stringify(value)}, 
        success:function(result){
            console.log(result);
    
                  }
      });
  
      
}


