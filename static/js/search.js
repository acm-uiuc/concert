var searchJustActive = false;
var userJustClicked = false;
var searchCurrentlyActive = false;

$(document).ready(function() {	
	windowUI.searchBox.select2({
	  allowClear: false,
	  multiple: true,
      maximumSelectionSize: 1,
	  ajax: {
	    url: '/search',
	    dataType: 'json',
	    data: function (params) {
	      return {
	        q: params.term, // search term
	        part: 'snippet',
	        maxResults: 15
	      };
	    },
	    processResults: function (data, params) {
	      // Filter by results with video ids
	      //console.log(data.items);
	      return {
	        results: data.items
	      };
	    },
	    cache: true
	  },
	  placeholder: 'Search for a Youtube or SoundCloud Video',
	  escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
	  minimumInputLength: 1,
	  templateResult: formatVideo,
	  templateSelection: formatVideoSelection,
	}).on("select2:select", function() {
		if (!userJustClicked) {
			searchJustActive = true;
		}
		document.activeElement.blur();
	}).on("select2:opening", function() {
		windowUI.searchBox.val(null).trigger('change');
		searchCurrentlyActive = true;
	}).on("select2:close", function() {
		searchCurrentlyActive = false;
	});

	if (!loggedin) {
		windowUI.searchBox.select2('enable', false);
		windowUI.searchBox.select2({
			placeholder: 'Please login to add to the queue'
		});
	}
});

function formatVideo (video) {
	if (video.loading) {
		return video.text;
	}

	var markup = 
 	"<div class='select2-result-repository clearfix'>" +
	"<div class='select2-result-repository__avatar'><img src='" + video.snippet.thumbnails.high.url + "' /></div>" +
	"<div class='select2-result-repository__meta'>" + 
	"<div class='select2-result-repository__title'>" + video.snippet.title + "</div>" +
	"<div class='select2-result-repository__description'>" + video.trackType + "</div></div>";

	var resultItem = $(markup);
	resultItem.on('mouseup', function(evt) {
		userJustClicked = true;
	});

	return resultItem;
}

function formatVideoSelection (video) {
	if (video.trackType == "SoundCloud") {
		return video.snippet.url;
	}
	return "https://www.youtube.com/watch?v=" + video.id;
}