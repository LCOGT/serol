/* globals $ rivetsBindings rivets apiRoot refreshTable */
'use strict';
var profile = {
  username: ''
};

var apiRoot = 'https://observe.lco.global/api/';

// rivets.bind($('#profile'), profile);

// $.ajaxPrefilter(function(options, originalOptions, jqXHR){
//   if(options.url.indexOf('lco.global/') >= 0 && localStorage.getItem('token')){
//     jqXHR.setRequestHeader('Authorization', 'Token ' + localStorage.getItem('token'));
//   }
// });

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

function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  var expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
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
