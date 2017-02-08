    function tweet()
    {
       var loc = window.location.href;
       var wind=  window.open("https://twitter.com/intent/tweet?url=" + loc + "&text=I am participating in #blackFridayDataHack. ", "_blank");
       wind.focus();
    }
    function fb()
    {
       var loc = window.location.href;
       var wind=  window.open("https://www.facebook.com/sharer/sharer.php?u="+loc, "_blank");
       wind.focus();
    }
