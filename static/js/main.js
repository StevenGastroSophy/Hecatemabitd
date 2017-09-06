 //選單
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
 //選單應對螢幕放大縮小 
  $(window).resize(function() {
        var wdth=$(window).width();
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
	return false;
    });
//選單內選項的捲動特效
$(document).ready(function() {
    $('#products_index-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#products_index').offset().top - 50}, 800);
    });
    $('#products_products-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#products_products').offset().top - 50}, 800);
    });
    $('#flowchart-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#flowchart').offset().top - 60}, 800);
    });
    $('#aboutme-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#aboutme').offset().top - 60}, 800);
    });
	$('#footer_index-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#footer_index').offset().top - 60}, 800);
    });
	$('#footer_products-click').click(function(){ 
        $('html,body').animate({
	        scrollTop:$('#footer_products').offset().top - 60}, 800);
    });
});
 
// 次級選單
  $('.sub-menu').click(function(){
  	$(this).children('.children').slideToggle();
  return false;
  })

});

//接收server端傳來的上線狀態並改變#hecate_status
$(document).ready(function() {
    // Use a "/test" namespace.
    // An application can open a connection on multiple namespaces, and
    // Socket.IO will multiplex all those connections on a single
    // physical channel. If you don't care about multiple channels, you
    // can set the namespace to an empty string.
    namespace = '/test';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);


    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('my_response', function(msg) {
	    if (msg.status == 'ONLINE') {
            $('#hecate_status span').css('color','#39A735');
			$('#status').text('ONLINE');
			$('.channel').css('visibility','visible');
			$('h2.channel').text(msg.channel);
  	    }else{
            $('#hecate_status span').css('color','#c1403b');
		    $('#status').text('OFFLINE');
			$('.channel').css('visibility','hidden');
			$('h2.channel').text('');
  	    }
    });

}); 

//購物車
$( function() {
    var dialog, form,	
    name = $( "#name" ),
    price = $( "#price" ),
    quantity = $( "#quantity" );
 
//將商品加入購物車清單 
  function addcart() {
    $( "#users tbody" ).append( "<tr style=\"height: 3em;\">" +
      "<td>" + name.text() + "</td>" +
      "<td>" + price.text().replace('$','') + "</td>" +
      "<td style=\"text-align: right; cursor: pointer;\">" + quantity.text().replace('個', '') + "</td>" +
	  "<td class=\"remove\" style=\"text-align: center; font-size: 1.6em; cursor: pointer;\">" + "<i class=\"fa fa-times\"></i>" + "</td>" +
      "</tr>" );
  }; 

//計算購物車清單內的加總  
  function sumup() {
	var total = 0;
	var totalquantity = 0;
    $( "#users tbody tr td:nth-child(4n-2)" ).each(function(){
		var q = parseInt($(this).next().text());
		totalquantity += q;
		if (isNaN(parseInt($(this).text().replace('$','').split('萬',2)[1]))) {
	      var i = (parseInt($(this).text().replace('$','').split('萬',1))*10000)*q;
		}
		else {
		  var i = (parseInt($(this).text().replace('$','').split('萬',1))*10000 + parseInt($(this).text().replace('$','').split('萬',2)[1]))*q;
		}
		total += i;
    })
    if (parseInt(total%10000) !=0){
	    var underTenThousand = parseInt(total%10000).toString();
	}
	else {
	    var underTenThousand = '';
	}
	var totalmabistyle = [ parseInt(total/10000).toString(), underTenThousand];
	$('#totalamount').text(totalmabistyle.join('萬'));
	$('#CartCount').text(totalquantity);
  }; 
 
  dialog = $( "#dialog-form" ).dialog({
    autoOpen: false,
    height: 300,
    width: 271,
    modal: true,
	position: { my: "center-9%", at: "center", of: window  } ,
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
//按下購物車按鈕 
  $( "#btn_cart" ).on( "click", function() {
	$("#dialog-form").parent().css({position : "fixed" }).end();
    dialog.dialog( "open" );
  }); 
//按下加入購物車  
  $( "#add-cart" ).button().on( "click", function() {
	$.blockUI({
        message: '<h1>加入購物車..</h1>',		
		css: {
            border: 'none',
            padding: '15px',
			width: '50%',
            left: '25%',			
            backgroundColor: '#FFBF00',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            color: '#191970'
        },
		overlayCSS:  { 
            backgroundColor: '#000000', 
            opacity:         0.6, 
            cursor:          'wait' 
        },
		// 淡入的時間.單位為毫秒200
		fadeIn:  200, 
        // 淡出的時間.單位為毫秒400 
        fadeOut: 400, 
	});
    addcart();
	sumup();
	UpdateSession();
	setTimeout($.unblockUI, 600);
	setTimeout(function () {dialog.dialog( "open" )}, 800);
  return false;
  }); 
//按下購物車清單內的移除鈕 
  $( "#users" ).on( "click", '.remove', function() {
	$.blockUI({
        message: '<h1>移除物品..</h1>',		
		css: {
            border: 'none',
            padding: '15px',
			width: '50%',
            left: '25%',			
            backgroundColor: '#FFBF00',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            color: '#191970'
        },
		overlayCSS:  { 
            backgroundColor: '#000000', 
            opacity:         0.6, 
            cursor:          'wait' 
        },
		// 淡入的時間.單位為毫秒200
		fadeIn:  200, 
        // 淡出的時間.單位為毫秒400 
        fadeOut: 400, 
	});
    $(this).closest('tr').remove();
	sumup();
	UpdateSession();
	//if ($('#CartCount').text() == '0') {
    //  setTimeout(function(){window.location.href='./products'}, 200);
	//}
	setTimeout($.unblockUI, 600);
  return false;
  }); 
});
//將購物車的內容用post傳回server更新session
function UpdateSession() {
	var namelist = [];
	var pricelist = [];
	var quantitylist = [];
	var totalamount = $('#totalamount').text();
	var CartCount = $('#CartCount').text();
	var count = 0;
    $( "#users tbody tr td" ).each(function(){
		count += 1;
		switch(count%4){
		  case 0:
		    //抓到移除紐,不做事
            break;
          case 1:
            namelist.push($(this).text());		  
            break;
		  case 2:
		    pricelist.push($(this).text());
			break;
		  case 3:
		    quantitylist.push($(this).text());
			break;
		}
    });
    $.post("/_update_cart", { 'namelist[]':namelist, 'pricelist[]':pricelist, 'quantitylist[]':quantitylist, totalamount:totalamount, CartCount: CartCount});
}