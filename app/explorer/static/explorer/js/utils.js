var site_codes = {
  'coj' : 'Siding Spring, Australia',
  'ogg' : 'Haleakala, Hawaii',
  'tfn' : 'Tenerife, Canary Islands',
  'cpt' : 'Sutherland, South Africa',
  'lsc' : 'Cerro Tololo, Chile',
  'elp' : 'McDonald, Texas'
}

var DateDiff = {

    inDays: function(d1, d2) {
        var t2 = d2.getTime();
        var t1 = d1.getTime();

        return parseInt((t2-t1)/(24*3600*1000));
    },

    inWeeks: function(d1, d2) {
        var t2 = d2.getTime();
        var t1 = d1.getTime();

        return parseInt((t2-t1)/(24*3600*1000*7));
    },

    inHours: function(d1, d2) {
        var t2 = d2.getTime();
        var t1 = d1.getTime();

        return parseInt((t2-t1)/(3600*1000));
    },

    inMinutes: function(d1, d2) {
        var t2 = d2.getTime();
        var t1 = d1.getTime();
        var dt = (t2-t1)/(3600*1000);
        var hours = parseInt(dt);
        var imins = parseInt((dt - hours)*60);

        if (String(imins).length == 1){
          return "0"+String(imins);
        } else {
          return imins ;
        }
    },

    inMonths: function(d1, d2) {
        var d1Y = d1.getFullYear();
        var d2Y = d2.getFullYear();
        var d1M = d1.getMonth();
        var d2M = d2.getMonth();

        return (d2M+12*d2Y)-(d1M+12*d1Y);
    },

    inYears: function(d1, d2) {
        return d2.getFullYear()-d1.getFullYear();
    }
}

function shuffle(array) {
  /*
  Fisher-Yates shuffle algorithm
  */
  var m = array.length, t, i;

  // While there remain elements to shuffle…
  while (m) {

    // Pick a remaining element…
    i = Math.floor(Math.random() * m--);

    // And swap it with the current element.
    t = array[m];
    array[m] = array[i];
    array[i] = t;
  }

  return array;
}

function get_qs(n) {
    var half = location.search.split(n + '=')[1];
    return half !== undefined ? decodeURIComponent(half.split('&')[0]) : null;
}

function update_status(requestid) {
  $.getJSON('/api/status/'+requestid+'/')
    .done(function(data){
      window.location.replace(redirect_url);
      console.log("DONE"+data);
    })
    .fail(function(data){
      console.log("FAIL "+data);
    });
    return;
}

function status_request(requestid, token) {
  var data;
  $.ajax(
    {
    url:'https://observe.lco.global/api/requestgroups/'+requestid+'/',
    type: "GET",
    headers: {"Authorization": "Token "+token},
    dataType: 'json',
    contentType: 'application/json'})
    .done(function(rdata){
      data = rdata
      if (rdata['state'] == 'PENDING' ){
        status_userrequest(rdata['requests'][0]['id'], token);
      } else if (rdata['state'] == 'COMPLETED' || rdata['state'] == 'WINDOW_EXPIRED' || rdata['state'] == 'CANCELED'){
        update_status(requestid);
      }
      console.log("DONE"+data);
    })
    .fail(function(rdata){
      resp_tmp=rdata;
      console.log("FAIL "+rdata);
    });
    return data;
}

function status_userrequest(requestid, token) {
  var data;
  $.getJSON('https://observe.lco.global/api/requests/'+requestid+'/observations/?exclude_canceled=true',
    {
    dataType: 'json',
    contentType: 'application/json'})
    .done(function(rdata){
      if (rdata.length > 0){
        var d2 = new Date(rdata[0]['start']);
        var d1 = new Date();
        var flextime = update_date(DateDiff.inDays(d1,d2), DateDiff.inHours(d1,d2), DateDiff.inMinutes(d1,d2));
        var site = site_codes[rdata[0]['site']];
        console.log("SCHEDULED"+rdata);
        $('.calendar-outer .info').html(flextime['units']);
        $('.calendar-inner .info').html(flextime['number']);
        update_site(rdata[0]['site']);
        $("."+rdata[0]['site']).addClass('location-highlight');
      } else {
        $('#location-text').html("Hmmm. I'll need to think about this. Check back later!");
        console.log("NOT SCHEDULED YET");
      }
      data = rdata
    })
    .fail(function(rdata){
      $('#location-text').html("Hmmm. I'm having trouble updating that.");
      console.log("FAIL "+rdata['detail']);
    });
    return data;
}


function get_colour_image(token, frameid, mode){
  $.when(
    $.get({url:'https://thumbnails.lco.global/'+frameid+'/?color=true&width=600&height=600',
          headers: {'Authorization': 'Token '+token},
          dataType: 'json',
          contentType: 'application/json'}
        )
      .done(function(data){
        img_url = data.url;
        if (mode == 'analyser'){
            $("#img-holder").attr('src',img_url);
        } else {
          arrange_images(img_url);
        }
      })
      .fail(function(rdata){
        console.log("FAILED to get thumbnail");
      })
    );
}

function arrange_images(url){
    images = shuffle(images).slice(0,3);
    images.push({'mine':true, 'url':url});
    images = shuffle(images);
    for (i=0;i<4;i++){
      $("#img-"+i).attr('src',images[i]['url']);
      $("#img-"+i).data('mine',images[i]['mine']);
    }
    $("img.identify-image").on('click', function(d){
      if ($(this).data('mine') == true){
        show_identify_answer('.identify-yes');
      } else {
        show_identify_answer('.identify-no');
      }
    });
  }

function show_identify_answer(class_id){
  $(class_id).show();
  $(class_id).addClass('grow');
  $(".grow").on('transitionend webkitTransitionEnd oTransitionEnd otransitionend MSTransitionEnd',
    function() {
         $(class_id).removeClass('grow');
         $(class_id).hide();
         if (class_id == ".identify-yes") { window.location.replace(redirect_url);}
    });
}

function update_date(days, hours, minutes){
  var number;
  var units;
  if  (days >0){
    number = days;
    units = "days";
  }else if (hours >1){
    number = hours;
    units = "hours";
  }else{
    number = minutes;
    units = "mins";
  }
  return {'number':number, 'units': units};
}

function update_site(siteid){
  var site = site_codes[siteid];
  $("."+siteid).addClass('location-highlight');
  $('#location-text').html(site)
}

function startEnd(date) {
  var end = new Date(date);
  end.setDate(end.getDate() + 7);
  return end.toISOString();
}

function submit_to_serol(data, redirect_url){
    var url = '/api/schedule/';
    console.log('In Submit to Serol')
		$.ajax({
			url: url,
			method: 'POST',
			cache: false,
			data: data,
			error: function(e){
				console.log('Error: '+e[0]);
				$('.modal-title').html("Error!");
				$('.modal-body').html("<p>Sorry, there was a problem submitting your request. Please try later.</p>");
			},
			success: function(data){
        $('#accept_button').attr('href',redirect_url);
        $('#accept_button').show();
				$('.modal-title').html("Success!");
				$('.modal-body').html("<p>Your image will be ready in a few days.</p>");
        $('#submit_button').hide();
        $('#submit_button').prop("disabled", true);
        $('#close_button').prop("disabled", true);
        window.setTimeout(function(){
          window.location.replace(redirect_url);
        },5000);

			}
		});
	}

  function get_facts() {
    var data;
    $.getJSON('/api/facts/',
      {
      dataType: 'json',
      contentType: 'application/json'})
      .done(function(rdata){
        setInterval(function() {
          show_facts(rdata);
        }, 10000);
      })
      .fail(function(rdata){
        console.log("FAIL "+rdata['detail']);
      });
      return data;
  }

  function show_facts(facts) {
    var index = Math.floor(Math.random() * facts.length);
    $(".fact-box p").html(facts[index]['desc']);
  }
