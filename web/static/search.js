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
function updateStats(artist) {
  console.log("get stats for", artist.id);

  let infoMsg = $('tr#' + artist.id + ' td.info-msg')

  $.getJSON(apiUrl + '/stats/' + artist.id, function (data) {

	if (data.pending) {
		let s = infoMsg.text()
		if (s.startsWith('Waiting for results')) {
			s = s.replace(/\.*$/, '.'.repeat((s.substring(19).length + 1) % 6));
			infoMsg.text(s);
		}
		setTimeout(updateStats, 5000, artist);

	} else {
		if (data.stats.nlyrics > 0) {
			infoMsg.remove();

			let tr = $('tr#' + artist.id)
			let wc = data.stats.wordcount;

			tr.append($('<td>' + wc.min + '</td>'));
			tr.append($('<td>' + wc.max + '</td>'));
			tr.append($('<td>' + Math.round(wc.avg) + '</td>'));
			tr.append($('<td>' + Math.round(wc.std) + '</td>'));

			let cb = tr.find('input')
			cb.show()
			cb.change(activatePlotButtons)
		} else {
			infoMsg.text("No lyrics found");
		}
    }
  }).fail(function() {
    infoMsg.text("An error has occured");
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

  updateStats(artist);

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
