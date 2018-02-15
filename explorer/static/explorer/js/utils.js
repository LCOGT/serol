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

function update_status(requestid, token) {
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
    url:'https://observe.lco.global/api/userrequests/'+requestid+'/',
    type: "GET",
    headers: {"Authorization": "Token "+token},
    dataType: 'json',
    contentType: 'application/json'})
    .done(function(rdata){
      data = rdata
      if (rdata['state'] == 'PENDING' && rdata['requests'].length > 0){
        status_userrequest(rdata['requests'][0]['id'], token);
      } else if (rdata['state'] == 'COMPLETED' || rdata['state'] == 'WINDOW_EXPIRED' || rdata['state'] == 'CANCELED'){
        update_status(requestid, token);
      }

      serol_alert_animation();
        setTimeout(function(){
          serol_end_alert();
        }, 5000);
      console.log("DONE"+data);
    })
    .fail(function(rdata){
      resp_tmp=rdata;
      console.log("FAIL "+rdata);
    });
    return data;
}

function status_userrequest(userrequestid, token) {
  var data;
  $.getJSON('https://observe.lco.global/api/requests/'+userrequestid+'/blocks/?canceled=false',
    {headers: {'Authorization': 'Token '+token},
    dataType: 'json',
    contentType: 'application/json'})
    .done(function(rdata){
      if (rdata.length > 0){
        var d2 = new Date(rdata[0]['start']);
        var d1 = new Date();
        var flexytime = update_date(DateDiff.inDays(d1,d2), DateDiff.inHours(d1,d2), DateDiff.inMinutes(d1,d2));
        var site = site_codes[rdata[0]['site']];
        console.log("SCHEDULED"+rdata);
        $('.bubble').html("<p>Your picture will be taken in <strong>"+flexytime+"</strong> by a telescope in <strong>"+site+"</strong>");
        update_site();
      } else {
        $('.bubble').html("<p>Hmmm. I'll need to think about this. Check back later!</p><p>I'll email you when I have your picture, too.</p>");
        console.log("NOT SCHEDULED YET");
      }
      data = rdata
    })
    .fail(function(rdata){
      console.log("FAIL "+rdata['detail']);
    });
    return data;
}

function serol_alert_animation(){
  $('.serol-antenna').addClass('serol-antenna-flash');
  $('.serol-pupil-normal').toggle();
  $('.serol-pupil-shock').toggle();
  $('.serol-mouth-normal').toggle();
  $('.serol-mouth-shock').toggle();
}

function serol_end_alert(){
  $('.serol-antenna').removeClass('serol-antenna-flash');
  $('.serol-pupil-normal').toggle();
  $('.serol-pupil-shock').toggle();
  $('.serol-mouth-normal').toggle();
  $('.serol-mouth-shock').toggle();
}

function get_colour_image(token, frameid, mode){
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
    });
}

function arrange_images(url){
    images = shuffle(images).slice(0,3);
    images.push({'mine':true, 'url':url});
    images = shuffle(images);
    for (i=0;i<4;i++){
      console.log(images[i]['url']);
      $("#img-"+i).attr('src',images[i]['url']);
      $("#img-text-"+i).data('mine',images[i]['mine']);
    }
    $(".identify-text").on('click', function(d){
      if ($(this).data('mine') == true){
        show_identify_answer('.identify-yes');
        console.log('YES')
      } else {
        show_identify_answer('.identify-no');
        console.log('NO');
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
  var txt;
  if  (days >0){
    txt = days+" days";
  }else if (hours >1){
    txt = hours+" hours";
  }else{
    txt = minutes+" mins";
  }
  return txt;
}

function update_site(){
  var txt = '<i class="far fa-hourglass-start fa-w-16 fa-3x fa-fw"></i>';
  $('#request-site').html(txt)
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
				$('.modal-body').html("<p>Your image will be ready in a few days.</p><img src='https://lco.global/files/edu/serol/serol_holding_cosmic_objects_sm.png'>");
        $('#submit_button').hide();
        $('#submit_button').prop("disabled", true);
        $('#close_button').prop("disabled", true);
        window.setTimeout(function(){
          window.location.replace(redirect_url);
        },5000);

			}
		});
	}

  function submit_request(obj, token){
    var target = {
      "type": "SIDEREAL",
      "name": obj.name,
      "ra": obj.ra,
      "dec": obj.dec,
      "equinox": "J2000",
      "epoch": 2000.0
    }
    var molecules = [
                {
                "type": "EXPOSE",
                "instrument_name": "0M4-SCICAM-SBIG",
                "filter": "rp",
                "exposure_time": 30.0,
                "exposure_count": 1,
                "bin_x": 2,
                "bin_y": 2,
                "defocus": 0.0,
              }
    ]
    var timewindow = {
            "start": start.toISOString().substr(0,19),
            "end": end.substr(0,19),
      }
    var request = {
      "location":{"telescope_class":"0m4"},
      "constraints":{"max_airmass":2.0},
      "target": target,
      "molecules": molecules,
      "windows": [timewindow],
      "observation_note" : "Serol",
      "type":"request"
    }
    var data = {
        "group_id": "sxe_201708_001",
        "proposal": "LCOEPO2014B-010",
        "ipp_value": 1.05,
        "operator": "SINGLE",
        "observation_type": "NORMAL",
        "requests": [request],
    }
    $.ajax({
      url: 'https://observe.lco.global/api/userrequests/',
      type: 'post',
      data: JSON.stringify(data),
      headers: {'Authorization': 'Token '+token},
      dataType: 'json',
      contentType: 'application/json'})
      .done(function(resp){
        console.log("DONE"+resp);
      })
      .fail(function(resp){
        console.log("FAIL "+resp);
      });
  }
