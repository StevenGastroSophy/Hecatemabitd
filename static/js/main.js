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

  //shopcart
  $( function() {
    var dialog, form,	
    name = $( "#name" ),
    price = $( "#price" ),
    quantity = $( "#quantity" );
  
  function addcart() {
    $( "#users tbody" ).append( "<tr>" +
      "<td>" + name.text() + "</td>" +
      "<td>" + price.text() + "</td>" +
      "<td>" + quantity.text() + "</td>" +
      "</tr>" );

  }
 
  dialog = $( "#dialog-form" ).dialog({
    autoOpen: false,
    height: 300,
    width: 271,
    modal: true,
	position: { my: "center-20%", at: "center", of: window  } ,
    buttons: {
	  '結帳': function() {
        dialog.dialog( "close" );
      },
      '繼續購買': function() {
        dialog.dialog( "close" );
      },
    },
    close: function() {
      form[ 0 ].reset();
    }
  });
  
 
  form = dialog.find( "form" ).on( "submit", function( event ) {
    event.preventDefault();
  });
 
  $( "#btn_cart" ).on( "click", function() {
	$("#dialog-form").parent().css({position : "fixed" }).end();
    dialog.dialog( "open" );
  });
  $( "#add-cart" ).button().on( "click", function() {
    addcart();
	$('#CartCount').text(parseInt($('#CartCount').text())+1);
	
    var total = 0;
	var totalquantity = 0;
    $( "#users tbody tr td:nth-child(3n-1)" ).each(function(){
		if (isNaN(parseInt($(this).text().replace('$','').split('萬',2)[1]))) {
	      var i = parseInt($(this).text().replace('$','').split('萬',1));
		}
		else {
		  var i = parseInt($(this).text().replace('$','').split('萬',1)) + parseInt($(this).text().replace('$','').split('萬',2)[1]);
		}
		total += i;
		totalquantity += 1;
    })
	$('#totalamount').text(total.toString()+'萬');
	$('#CartCount').text(totalquantity)
	
	dialog.dialog( "open" );
  });
});