var searchJustActive = false;

$(document).ready(function() {	
	$("#url-textbox").select2({
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
	        maxResults: 10
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
	  placeholder: 'Search for a Youtube Video',
	  escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
	  minimumInputLength: 1,
	  templateResult: formatVideo,
	  templateSelection: formatRepoSelection,
	}).on("select2:select", function() {
		searchJustActive = true;
		document.activeElement.blur();
	});

	if (!loggedin) {
		$("#url-textbox").select2('enable', false);
		$("#url-textbox").select2({
			placeholder: 'Please login to add to the queue'
		});
	}
});

function formatVideo (video) {
	if (video.loading) {
		return video.text;
	}
	console.log(video);

	var markup = 
 	"<div class='select2-result-repository clearfix'>" +
	"<div class='select2-result-repository__avatar'><img src='" + video.snippet.thumbnails.high.url + "' /></div>" +
	"<div class='select2-result-repository__meta'>" + 
	"<div class='select2-result-repository__title'>" + video.snippet.title + "</div>" +
	"<div class='select2-result-repository__description'>" + video.trackType + "</div></div>";

	return markup;
}

function formatRepoSelection (video) {
	if (video.trackType == "SoundCloud") {
		return video.snippet.url;
	}
	return "https://www.youtube.com/watch?v=" + video.id;
}