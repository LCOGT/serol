/* globals $ rivetsBindings rivets apiRoot refreshTable */
'use strict';
var profile = {
  username: ''
};

var apiRoot = 'https://observe.lco.global/api/';

// rivets.bind($('#profile'), profile);

$.ajaxPrefilter(function(options, originalOptions, jqXHR){
  if(options.url.indexOf('lco.global/') >= 0 && localStorage.getItem('token')){
    jqXHR.setRequestHeader('Authorization', 'Token ' + localStorage.getItem('token'));
  }
});

function getProposals(){
  $.getJSON(apiRoot + 'profile/', function(data){
    profile.username = data.username || '';
  });
}

function login(username, password, callback){
  $.ajax({
    url: apiRoot + 'api-token-auth/',
    type: 'post',
    data:     {
          'username': username,
          'password': password
        },
    dataType: 'json',
    success: function(data){
      localStorage.setItem('token', data.token);
      console.log("stored token"+data.token);
      //getProposals();
      callback(true);
    },
    fail: function(){
      callback(false);
    }
  });
}

function logout(){
  localStorage.removeItem('token');
  profile.username = '';
}


// Make sure ajax POSTs get CSRF protection
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = $.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      var csrftoken = getCookie('csrftoken');
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
    }
  }
});
