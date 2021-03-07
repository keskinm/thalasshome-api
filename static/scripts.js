

function validate() {
    var value = document.getElementById("choix_locations").value;
    console.log('jedebug!')
    console.log(value);

    $.ajax({  
        type : 'POST',
        url : "{{url_for('trying')}}",
        // url : "192.168.1.29:5000/trying",
        data : {"data": JSON.stringify(value)}, 
        success:function(result){
            console.log(result);
    
                  }
      });
  
      
}


