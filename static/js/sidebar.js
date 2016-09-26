var page_width = $(document).width();
 if(page_width > 880)
 {
     $('#sidebar').affix({
       offset: {
         top: 335, bottom :function () {
                 return (this.bottom == $("footer").offset().top + 200)
                 }
       }
     });
 }
 else{
     $('#sidebar').affix({
       offset: {
         top: 500, bottom :function () {
                 return (this.bottom == $("footer").offset().top)
                 }
       }
     });
      
 }
 /* activate scrollspy menu */
 var $body   = $(document.body);
 var navHeight = $('.navbar').outerHeight(true) + 10;
 
 $body.scrollspy({
 	target: '#leftCol',
 	offset: navHeight
 });
 $("#sidebar.affix-top").height($(window).height()-50);
 
 /* smooth scrolling sections */
 $('a[href*=#]:not([href=#])').click(function() {
     if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
       var target = $(this.hash);
       target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
       if (target.length) {
         $('html,body').animate({
           scrollTop: target.offset().top - 50
         }, 1000);
         return false;
       }
     }
 });

