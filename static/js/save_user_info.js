
   $('#myModal4').modal({backdrop: 'static', keyboard: false}) ;
       var a;
       var des;
       $("#submit-location").click(function(){
         var data = new FormData($('#location-submissions').get(0));
         $.ajax({
             url: '/user/save_location',
             type: 'POST',
             data: data,
             cache: false,
             processData: false,
             contentType: false,
             success: function(data) {
                if(data["error"] == "true")
                {
                   $("#myModal4").modal("hide");
                   $("#modal-header1").html("Success");
                   $("#modal-body1").html("Congratulations, Your location has been set.");
                   $('#myModal1').modal('show');
                }
                else{
                   $("#myModal4").modal("hide");
                   $("#modal-header1").html("Success");
                   $("#modal-body1").html(data["message"]);
                   $('#myModal1').modal('show');
                }
             },
             error : function(data){
                   $("#modal-body").html("Some error occured");
                   $('#myModal').modal('show');
             }
         });
        });
