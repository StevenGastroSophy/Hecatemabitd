  //navbar
$(document).ready(function(){

	var val = 1;

  $(".nav-bar").click(function(){


  	if (val == 1) {

	  	$("header nav").animate({
	    	'left' : '0'
	    });
		$(".nav-bar i").toggleClass("fa fa-bars").toggleClass("fa fa-close");
	    val = 0;
  	}else{
  		val = 1;
  		$("header nav").animate({
		    'left' : '-100%'
		},"fast");
		$(".nav-bar i").toggleClass("fa fa-close").toggleClass("fa fa-bars");
  	}



    return false;
  });
  
  $(window).resize(function() {
        wdth=$(window).width();
		if (wdth > 800) {
		$("header nav").animate({
	    	'left' : '0'
	    });
	}else {
        $("header nav").animate({
		    'left' : '-100%'
		},"fast");
		val = 1;
    }
	    var navclass = $(".nav-bar i").attr("class");
		if (navclass == "fa fa-close") {
		$(".nav-bar i").toggleClass("fa fa-close").toggleClass("fa fa-bars");
	}
    });
   //scroll
$(document).ready(function() {
    $('#products-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#products').offset().top - 50}, 800);
    });
    $('#flowchart-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#flowchart').offset().top - 60}, 800);
    });
    $('#aboutme-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#aboutme').offset().top - 60}, 800);
    });
	$('#contactus-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#contactus').offset().top - 60}, 800);
    });
});
 
  // submenu
  $('.sub-menu').click(function(){
  	$(this).children('.children').slideToggle();
  })

}); 