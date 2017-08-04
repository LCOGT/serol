function submit_to_serol(target, token){

		var url = '/schedule/';
		var data = {start:start.toISOString().substr(0,19),
					end:end.substr(0,19),
					aperture:'0m4', //obs_vals[0]['aperture'],
					object_name:target.name,
					object_ra:target.ra,
					object_dec:target.dec,
					filters:JSON.stringify(target.filters),
					token: token,
				};
		$.ajax({
			url: url,
			method: 'POST',
			cache: false,
			data: data,
			error: function(e){
				console.log('Error: '+e);
				var content = "<h3>Error!</h3><p>Sorry, there was a problem submitting your request. Please try later.</p>"
				$('#message-content').html(content);
				closePopup(delay='2000');
			},
			success: function(data){
				var content = "<h3>Success!</h3><p>Your image will be ready in the next week.</p><img src='http://lcogt.net/files/edu/serol/serol_sm.png'>"
				$('#message-content').html(content);
				closePopup(delay='2000');
				// Stop them from accidentally submitting a second time
				$('#observe_button').hide();

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
      "constraints":{"max_airmass":1.6},
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
    console.log(data)
    $.ajax({
      url: 'https://observe.lco.global/api/userrequests/',
      type: 'post',
      data: data,
      headers: {'Authorization': 'Token '+token},
      dataType: 'json',
      success: function(data){
        console.log(data);
      }
  });
  }
