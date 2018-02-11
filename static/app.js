var socket;
var currentUrl;
var currentSong;
var currentTime;
var currentEndTime;
var currentProgressInterval;

function updateProgress() {
    console.log("Called")
    currentTime += 1000;
    $('#progress-slider').val((currentTime/currentEndTime* 100).toString());
}

$(document).ready(function () {
    socket = io.connect('http://' + document.domain + ':' + location.port);
    console.log(document.domain);
    console.log(location.port);
    socket.on('connected', function(state) {
        updateClient(state);
    });

    //playing sample music for testing
    $('#play-pause-button').click(function(e) {
        /*if ($('#play-pause-button').hasClass('play') && currentUrl == null)
        {
            //replace with actual current song
            currentUrl = "music/-5slZHLSnow.mp3";
            socket.emit('play', currentUrl);            
        }
        else*/
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

    socket.on('download', function(state) {
        console.log("Download emitted");
        updateClient(state);
    });

    socket.on('download_error', function() {
        //TODO: Better error handling
        console.log("Invalid URL");
    });

    socket.on('play', function(state) {
        updateClient(state);
        $('#play-pause-button').addClass('pause');
        $('#play-pause-button').removeClass('play');
        clearInterval(currentProgressInterval);
        if(currentSong != null){
            currentProgressInterval = setInterval(updateProgress, 1000);
        }
    });

    socket.on('pause', function(state) {
        //change to toggle
        if ($('#play-pause-button').hasClass('play'))
        {
            currentProgressInterval = setInterval(updateProgress, 1000); 
        }
        else
        {
            clearInterval(currentProgressInterval);
        }

        updateClient(state);
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

    socket.on('position', function() {
        var curTime = jsonState.current_time;
        var totalTime = jsonState.duration;
        $('#progress-slider').val((curTime/totalTime * 100).toString());
    });

    
    function updateClient(state) {
        var jsonState = JSON.parse(state);
        if (jsonState != null)
        {
            console.log(jsonState);
            $('#volume-slider').val(jsonState.volume.toString());

            if(jsonState.media != null){
                currentSong = jsonState.current_track
                currentTime = jsonState.current_time;
                currentEndTime = jsonState.duration;
                $('#progress-slider').val((currentTime/currentEndTime * 100).toString());
            }else{
                currentSong = null;
                currentTime = 0;
                currentEndTime = 0;
            }

            if(jsonState.media != null && jsonState.is_playing == true){
                currentUrl = jsonState.media;
                $('#song-name').text(jsonState.current_track);
            } else{
                currentUrl = null;
                $('#song-name').text("None");
            }
    
            if (jsonState.is_playing && (jsonState.audio_status == "State.Playing" || jsonState.audio_status == "State.Opening")) {
                $('#play-pause-button').addClass('pause');
                $('#play-pause-button').removeClass('play');
            } else{
                $('#play-pause-button').addClass('play');
                $('#play-pause-button').removeClass('pause');
            }
        }
    }
});
