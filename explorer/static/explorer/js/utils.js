
function status_check(requestid, token) {
  $.getJSON('https://observe.lco.global/api/userrequests/'+requestid+'/',
    {headers: {'Authorization': 'Token '+token},
    dataType: 'json',
    contentType: 'application/json'})
    .done(function(resp){
      tmp = resp
      console.log("DONE"+resp);
    })
    .fail(function(resp){
      console.log("FAIL "+resp);
    });
}

function submit_to_serol(target, token, redirect_url){

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
				closePopup(delay='2000');
			},
			success: function(data){
				$('.modal-title').html("Success!");
				$('.modal-body').html("<p>Your image will be ready in the next week.</p><img src='https://lco.global/files/edu/serol/serol_holding_cosmic_objects_sm.png'>");
        window.location.replace(redirect_url);

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
