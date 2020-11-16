'use strict';

var searchInput = $('#search-input');
var results = $('#results');
var apiUrl = '/api';
var stats = $('#stats-table');
var timeoutSuggest;

stats.hide();

searchInput.on('input', function() {
  if (timeoutSuggest) {
    clearTimeout(timeoutSuggest);
  }
  timeoutSuggest = setTimeout(suggestions, 300);
});

function removeResults() {
  $('.result').remove();
}

function suggestions() {
  var term = searchInput.val();
  if (!term) {
    removeResults();
    return;
  }
  console.log("get suggestions for", term);
  $.getJSON(apiUrl + '/search/' + term, function (data) {
    removeResults();
    data.artists.forEach(function (artist) {
      var t = artist.name;
      if (artist.disambiguation) {
        t += '<span class="disambiguate">(' + artist.disambiguation + ')</span>';
      }
      var e = $('<li class="result">' + t + '</li>');
      results.append(e);
      e.click(function () {
        removeResults();
        stats.slideDown();
        getStats(artist);
      });
    });
  });
}
function getStats(artist) {
  if ($('tr#' + artist.id).length) {
    return;
  } 

  var r = '<td><input type="checkbox" class="select" id="' + artist.id + '"></td>'
  r += '<td>' + artist.name + '</td>'
  r += '<td colspan="4" class="info-msg">Waiting for results</td>'
  var e = $('<tr id="' + artist.id + '">' + r + '</tr')
  stats.append(e)

  let tr = $('tr#' + artist.id)
  let infoMsg = tr.find('td.info-msg')

  let cntr = setInterval(function() {
    let s = infoMsg.text()
	if (s.startsWith('Waiting for results')) {
		s = s.replace(/\.*$/, '.'.repeat((s.substring(19).length + 1) % 6));
		infoMsg.text(s);
	}
  }, 1000);

  console.log("get stats for", artist.id);

  $.getJSON(apiUrl + '/stats/' + artist.id, function (data) {

    if (data.stats.nlyrics > 0) {
        let wc = data.stats.wordcount;
        tr.find('td.info-msg').remove();
        tr.append($('<td>' + wc.min + '</td>'));
        tr.append($('<td>' + wc.max + '</td>'));
        tr.append($('<td>' + Math.round(wc.avg) + '</td>'));
        tr.append($('<td>' + Math.round(wc.std) + '</td>'));
        let cb = tr.find('input')
        cb.show()
        cb.change(activatePlotButtons)
    } else {
        tr.find('td.info-msg').text("No lyrics found");
    }
  }).fail(function() {
    tr.find('td.info-msg').text("An error has occured");
  }).always(function() {
    clearInterval(cntr);  
  });
}

function activatePlotButtons() {
  let selected = $('.select:checked').map(function(){return this.id;}).get()
  if (selected.length == 0) {
      $('.plotbutton').hide();
  } else if (selected.length == 1) {
      $('#histogram').show();
      $('#peralbum').show();
      $('#peryear').hide();
      $('#perarea').hide();
  }
  if (selected.length > 1) {
      $('#histogram').show();
      $('#peralbum').hide();
      $('#peryear').show();
      $('#perarea').show();
  }
}
$('.plot').click(function() {
    $('.plot').hide();
});
$('.plotbutton').click(function() {
  let selected = $('.select:checked').map(function(){return this.id;}).get()
  let ids = selected.join(',')
  $.getJSON(apiUrl + '/plot/' + this.id + '/' + btoa(ids), function (data) {
    $('.plot').attr('src', data.img);
    $('.plot').show();
  });
});
