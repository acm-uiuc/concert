let searchJustActive = false;
let userJustClicked = false;
let searchCurrentlyActive = false;

$(document).ready(() => {
    $("#url-textbox").select2({
        allowClear: false,
        multiple: true,
        maximumSelectionSize: 1,
        ajax: {
            url: '/search',
            dataType: 'json',
            data: (params) => {
                return {
                    q: params.term, // search term
                    part: 'snippet',
                    maxResults: 15,
                    timeout: 1
                };
            },
            processResults: (data, params) => {
                // Filter by results with video ids
                return { results: data.items };
            },
            cache: true
        },
        placeholder: 'Search for a song on Soundcloud or Youtube',
        escapeMarkup: markup => markup, // let our custom formatter work
        minimumInputLength: 1,
        templateResult: formatVideo,
        templateSelection: formatVideoSelection,
    }).on("select2:select", () => {
        if (!userJustClicked) {
            searchJustActive = true;
        }

        document.activeElement.blur();
    }).on("select2:opening", () => {
        $("#url-textbox").val(null).trigger('change');
        searchCurrentlyActive = true;
    }).on("select2:close", () => {
        searchCurrentlyActive = false;
    }).on('select2:closing', () => {
	if (userJustClicked) {
    	    return;
	}
	
	$('.select2-search__field').css('color', 'white');
	const currentQuery = $('.select2-search__field').prop('value');
    
        setTimeout(() => {
	    if(currentQuery && currentQuery.length) {
 		$('.select2-search__field').val(currentQuery);
        	$('.select2-search__field').css('color', 'black');
	    }
    	}, 0);
    });

    if (!isUserLoggedIn) {
        $("#url-textbox").select2('enable', false);
        $("#url-textbox").select2({
            placeholder: 'Please login to add to the queue'
        });
    }
});

function formatVideo(video) {
    if (video.loading) {
        return video.text;
    }

    const markup =
        "<div class='select2-result-repository clearfix'>" +
        "<div class='select2-result-repository__avatar'><img src='" + video.snippet.thumbnails.high.url + "' /></div>" +
        "<div class='select2-result-repository__meta'>" +
        "<div class='select2-result-repository__title'>" + video.snippet.title + "</div>" +
        "<div class='select2-result-repository__description'>" + video.trackType + "</div></div>";

    const resultItem = $(markup);
    resultItem.on('mouseup', (evt) => {
        userJustClicked = true;
    });

    return resultItem;
}

function formatVideoSelection(video) {
    if (video.trackType == "SoundCloud") {
        return video.snippet.url;
    }

    return "https://www.youtube.com/watch?v=" + video.id;
}
