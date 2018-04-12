$(document).ready(function() {
	$("#url-textbox").select2({
      allowClear: true,
      multiple: true,
      maximumSelectionSize: 1,
	  ajax: {
	    url: '/ytsearch',
	    dataType: 'json',
	    data: function (params) {
	      return {
	        q: params.term, // search term
	        part: 'snippet',
	        baseURL: "https://www.googleapis.com/youtube/v3/search",
	      };
	    },
	    processResults: function (data, params) {
	      // parse the results into the format expected by Select2
	      // since we are using custom formatting functions we do not need to
	      // alter the remote JSON data, except to indicate that infinite
	      // scrolling can be used
	      params.page = params.page || 1;

	      return {
	        results: data.items,
	        pagination: {
	          more: (params.page * 30) < data.total_count
	        }
	      };
	    },
	    cache: true
	  },
	  placeholder: 'Search for a Youtube Video',
	  escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
	  minimumInputLength: 1,
	  templateResult: formatVideo,
	  templateSelection: formatRepoSelection
	});
});

function formatVideo (video) {
	if (video.loading) {
		return video.text;
	}
	console.log(video)

	var markup = "<div class='select2-result-repository clearfix'>" +
	"<div class='select2-result-repository__avatar'><img src='" + video.snippet.thumbnails.high.url + "' /></div>" +
	"<div class='select2-result-repository__meta'>" +
	  "<div class='select2-result-repository__title'>" + video.snippet.title + "</div>";

	return markup;
}

function formatRepoSelection (repo) {
  return repo.full_name || repo.text;
}