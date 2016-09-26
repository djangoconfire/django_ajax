

               $("#firstmodal").modal('show');
               $("#firstmodal .modal-body").css("height",$(window).height()*0.7);
               var width =  $(".buttonss").width();
             
               $(".buttonss").css("margin-left", ($(window).width()*0.9 - width -100 )/2);
               var width =  $(".buttons").width();
               $(".buttons").css("margin-left", ($(window).width() * 0.9 - width )/2);
               $(".image").css("margin-left", ($(window).width() * 0.9 - 250 )/2);
               var height = $("#intro").height() ;
               $(".hid").css("display","none");
               var h = $(".modal-body").height();
               $(".image2").css("height", h*0.75);
                
               $(".clicks").hide();
               $("#intro").show();
               $("#view-welcome-next").click(function(){
                  $("#intro").hide();
                  $("#welcome").show();
               });     
               $("#view-intro-prev").click(function(){
                  $("#welcome").hide();
                  $("#intro").show();
               });     
               $("#view-prizes-next").click(function(){
                  $("#welcome").hide();
                  $("#prizes").show();
               });     
               $("#view-welcome-prev").click(function(){
                  $("#prizes").hide();
                  $("#welcome").show();
               });     
               $("#view-tour-next").click(function(){
                  $("#prizes").hide();
                  $("#tour").show();
               });     
               $("#view-prizes-prev").click(function(){
                  $("#tour").hide();
                  $("#prizes").show();
               });     
               $("#view-slack-next").click(function(){
                  $("#tour").hide();
                  $("#slack").show();
               });     
               $("#view-tour-prev").click(function(){
                  $("#slack").hide();
                  $("#tour").show();
               });

               $("#view-tour-prev1").click(function(){
                  $("#upload_solution").hide();
                  $("#tour").show();
               });

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
               $("#view-slack-prev").click(function(){
                  $("#final_rankings").hide();
                  $("#slack").show();
               });     
               $("#view-final_rankings-prev").click(function(){
                  $("#upload_solution").hide();
                  $("#final_rankings").show();
               });
               $("#view-upload_solution-prev").click(function(){
                  $("#leaderboard").hide();
                  $("#upload_solution").show();
               });
               $("#view-leaderboard-prev").click(function(){
                  $("#summary").hide();
                  $("#leaderboard").show();
               });
               $("#view-summary-prev").click(function(){
                  $("#last").hide();
                  $("#summary").show();
               });
               $("#view-final_rankings-next").click(function(){
                  $("#slack").hide();
                  $("#final_rankings").show();
               });
               $("#view-upload_solution-next").click(function(){
                  $("#final_rankings").hide();
                  $("#upload_solution").show();
               });
               $("#view-upload_solution-next1").click(function(){
                  $("#tour").hide();
                  $("#upload_solution").show();
               });
               $("#view-last-next").click(function(){
                  $("#summary").hide();
                  $("#last").show();
               });
               $("#view-leaderboard-next").click(function(){
                  $("#upload_solution").hide();
                  $("#leaderboard").show();
               });
               $("#view-summary-next").click(function(){
                  $("#leaderboard").hide();
                  $("#summary").show();
               });
               $("#ready-hack").click(function(){
                  $("#summary").hide();
////////process the logic here . close the modal box. and set online = true
                 $("#firstmodal").modal('hide');
               });
