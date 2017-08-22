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

function status_request(requestid, token) {
  var data;
  $.getJSON('https://observe.lco.global/api/userrequests/'+requestid+'/',
    {headers: {'Authorization': 'Token '+token},
    dataType: 'json',
    contentType: 'application/json'})
    .done(function(rdata){
      data = rdata
      if (rdata['state'] == 'PENDING' && rdata['requests'].length > 0){
        status_userrequest(rdata['requests'][0]['id'], token)
      }
      console.log("DONE"+data);
    })
    .fail(function(rdata){
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
        update_date(DateDiff.inDays(d1,d2), DateDiff.inHours(d1,d2), DateDiff.inMinutes(d1,d2));
        update_site(rdata[0]['site']);
      }
      console.log("SCHEDULED"+rdata);
      data = rdata
    })
    .fail(function(rdata){
      console.log("FAIL "+rdata['detail']);
    });
    return data;
}

function fetch_image(userrequestid, archivetoken){
  var data = {};
  $.getJSON('https://archive-api.lco.global/frames/?limit=1&offset=1&ordering=-id&REQNUM='+userrequestid,
    {headers: {'Authorization': 'Token '+token},
    dataType: 'json',
    contentType: 'application/json'})
    .done(function(rdata){
      if (rdata['results'].length > 0){
        data['frame'] = rdata['results'][0]['id'];
        data['url'] = rdata['results'][0]['url'];
      }
      console.log("Number of Images ="+rdata['results'].length);
    })
    .fail(function(rdata){
      console.log("FAIL "+rdata['detail']);
    });
    return data;
}

function update_date(days, hours, minutes){
  if  (days >0){
    $('#request-time').html(days+" days");
  }else if (hours >1){
    $('#request-time').html(hours+" hours");
  }else{
    $('#request-time').html(minutes+" mins");
  }
}

function update_site(site){
  var name = site_codes[site];
  $('#request-site').html(name)
}

function startEnd(date) {
  var end = new Date(date);
  end.setDate(end.getDate() + 7);
  return end.toISOString();
}

function submit_to_serol(target, token, challenge_id, redirect_url, csrftoken){
    var start = new Date();
    var end = startEnd(start);
		var url = '/api/schedule/';
		var data = {start:start.toISOString().substr(0,19),
					end:end.substr(0,19),
					aperture:'0m4', //obs_vals[0]['aperture'],
					object_name:target.name,
					object_ra:target.ra,
					object_dec:target.dec,
					filters:JSON.stringify(target.filters),
					token: token,
          csrfmiddlewaretoken: csrftoken,
          challenge:challenge_id
				};
		$.ajax({
			url: url,
			method: 'POST',
			cache: false,
			data: data,
			error: function(e){
				console.log('Error: '+e);
				$('.modal-title').html("Error!");
				$('.modal-body').html("<p>Sorry, there was a problem submitting your request. Please try later.</p>");
			},
			success: function(data){
				$('.modal-title').html("Success!");
				$('.modal-body').html("<p>Your image will be ready in the next week.</p><img src='https://lco.global/files/edu/serol/serol_holding_cosmic_objects_sm.png'>");
        $('#submit_button').html("Next >");
        $('#submit_button').attr('href',redirect_url);
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
