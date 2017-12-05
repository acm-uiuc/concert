var socket;
var currentUrl;

$(document).ready(function () {
    //socket = io.connect('http://' + document.domain + ':' + location.port);
    socket = io.connect('http://127.0.0.1:5000/');
    socket.on('connected', function(state) {
        updateClient(state);
    });

    //playing sample music for testing
    $('#play-pause-button').click(function(e) { 
        if ($('#play-pause-button').hasClass('play'))
            socket.emit('play', "music/-5slZHLSnow.mp3");
        else
            socket.emit('pause');
    });

    $('#skip-button').click(function(e) { 
        socket.emit('skip');
    });

    $('#previous-button').click(function(e) { 
        socket.emit('previous');
    });

    $("#volume-slider").on("input", function() {
        socket.emit('volume', parseInt(this.value));
    });

    $("#import-button").click(function(e) {
        if ($('#url-textbox').val().trim() != ""){
            currentUrl = $('#url-textbox').val();
            socket.emit('download', currentUrl);
            $('#url-textbox').val("");
        }
        else
            return false;
    });

    socket.on('download', function(queue) {
        console.log('bah');
        console.log(queue);
    });

    socket.on('download_error', function() {
        //TODO: Better error handling
        console.log("Invalid URL");
    });

    socket.on('play', function(state) {
        $('#play-pause-button').addClass('pause');
        $('#play-pause-button').removeClass('play');
        var jsonState = JSON.parse(state);
        $('#song-name').text(jsonState.current_track);
    });

    socket.on('pause', function() {
        $('#play-pause-button').addClass('play');
        $('#play-pause-button').removeClass('pause');
    });

    socket.on('skip', function(state) {
        updateClient(state);
    });

    socket.on('previous', function() {
        
    });

    socket.on('volume', function(state) {
        //pass in new volume data
        //$('#volume-slider').val(newVolume);
        //console.log(state["volume"]);

        var jsonState = JSON.parse(state);
        $('#volume-slider').val(jsonState.volume.toString());
    });

    
    function updateClient(state) {
        var jsonState = JSON.parse(state);
        if (jsonState != null)
        {
            $('#volume-slider').val(jsonState.volume.toString());
            $('#song-name').text(jsonState.current_track);
    
            if (!jsonState.is_playing) {
                $('#play-pause-button').addClass('pause');
                $('#play-pause-button').removeClass('play');
            }
        }
    }
});
