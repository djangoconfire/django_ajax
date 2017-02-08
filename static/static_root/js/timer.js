                 function startTimer(duration, display) {
                     var timer = duration, minutes, seconds;
                     setInterval(function () {
                         minutes = parseInt(timer / 60, 10)
                         seconds = parseInt(timer % 60, 10);
                         hours = minutes / 60;
                         minutes = parseInt(minutes % 60);
                         days = parseInt(hours / 24);
                         hours = parseInt(hours % 24 );
                 
                         minutes = minutes < 10 ? "0" + minutes : minutes;
                         seconds = seconds < 10 ? "0" + seconds : seconds;
                         if(days == 0 && minutes == 0 && hours == 0 && seconds == 0)
                          {
                                $("#days").text("Contest ended");
                          }
                         else{
                         display.text(days + " days, " + hours + ": " + minutes + ":" + seconds);
                         $("#days").text(days+"d") ;
                         $("#minutes").text(minutes+"m") ;
                         $("#hours").text(hours+"h") ;
                         $("#seconds").text(seconds+"s") ;
                         }
                        
                 
                         if (--timer < 0) {
                             timer = duration;
                         }
                     }, 1000);
                 }
