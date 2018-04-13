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
	        maxResults: 10,
	        baseURL: "https://www.googleapis.com/youtube/v3/search",
	      };
	    },
	    processResults: function (data, params) {
	      // Filter by results with video ids
		  var res = []
	      for (var i = 0; i < data.items.length; i++) {
	      	item = data.items[i];
	      	var videoId = item.id.videoId;
	      	item.id = videoId;
	      	if(item.id != undefined) {
	      		res.push(item);
	      	}
	      }

	      return {
	        results: res
	      };
	    },
	    cache: true
	  },
	  id: function(obj) {
	  	return obj.id;
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
		//$("#url-textbox").replaceWith("<div class=\"inner first\">Hello</div>");
	}
});

function formatVideo (video) {
	if (video.loading) {
		return video.text;
	}

	var markup = "<div class='select2-result-repository clearfix'>" +
	"<div class='select2-result-repository__avatar'><img src='" + video.snippet.thumbnails.high.url + "' /></div>" +
	"<div class='select2-result-repository__meta'>" +
	  "<div class='select2-result-repository__title style='display: none'>" + video.snippet.title + "</div>";

	return markup;
}

function formatRepoSelection (video) {
	return "https://www.youtube.com/watch?v=" + video.id;
}