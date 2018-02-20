var socket;
var currentUrl;
var currentSong;
var currentTime;
var currentEndTime;
var currentProgressInterval;
var list = $('#playlist');

function formatSeconds(time) {
    var minutes = Math.floor(time / 60);
    var seconds = time - minutes * 60;
    return str_pad_left(minutes,'0',2)+':'+str_pad_left(seconds,'0',2);
}

function str_pad_left(string,pad,length) {
    return (new Array(length+1).join(pad)+string).slice(-length);
}

function updateProgress() {
    //console.log("Called")
    currentTime += 1000;
    $('#progress-slider').val(currentTime/currentEndTime);
}

function createQueueItem(title, time, songPlaying) {
    var entry = document.createElement('li');
    if(songPlaying){
        entry.className += "playing";
    }
    var content = document.createElement('a');
    content.className += "track";
    content.innerText = title;
    var timeInfo = document.createElement('span');
    timeInfo.className += "time";
    timeInfo.innerText = formatSeconds(time/1000);
    entry.appendChild(content);
    entry.appendChild(timeInfo);
    return entry;
}

function reloadQueue(queued_songs){
    var len = queued_songs.length;
    list.empty();
    for(var i = 0; i < len; i++){
        var curSong = queued_songs[i];
        var newQueuedSong = createQueueItem(curSong.title, curSong.duration, false);
        list.append(newQueuedSong);
    }
}

$(document).ready(function () {
    socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connected', function(state) {
        updateClient(state);
    });

    $('#play-pause-button').click(function(e) {
        socket.emit('pause');
    });

    $('#next').click(function(e) { 
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

    socket.on('downloaded', function(state) {
        console.log("Download emitted");
        updateClient(state);
    });

    socket.on('download_error', function() {
        //TODO: Better error handling
        console.log("Invalid URL");
    });

    socket.on('stopped', function(state) {
        console.log("Stopped");
        updateClient(state);
    });

    socket.on('played', function(state) {
        updateClient(state);
        $('#play-pause-button').addClass('pause');
        $('#play-pause-button').removeClass('play');
        clearInterval(currentProgressInterval);
        currentProgressInterval = setInterval(updateProgress, 1000);
    });

    socket.on('heartbeat', function(state) {
        console.log("HEARTBEATING");
        updateClient(state);
    })

    socket.on('paused', function(state) {
        //change to toggle
        var playState = JSON.parse(state);
        if (playState.is_playing && (playState.audio_status == "State.Playing" || playState.audio_status == "State.Opening")){
            currentProgressInterval = setInterval(updateProgress, 1000); 
            $('#play-pause-button').removeClass('fa-play').addClass('fa-pause');
        }
        else{
            clearInterval(currentProgressInterval);
            $('#play-pause-button').addClass('fa-play').removeClass('fa-pause');
        }

        currentTime = playState.current_time;
        currentEndTime = playState.duration;
    });

    socket.on('skipped', function(state) {
        updateClient(state);
    });

    socket.on('previous', function() {
        
    });

    socket.on('volume_changed', function(volumeResponse) {
        volumeState = JSON.parse(volumeResponse)
        $('#volume-slider').val(volumeState.volume);
    });

    socket.on('position_changed', function() {
        var curTime = jsonState.current_time;
        var totalTime = jsonState.duration;
        $('#progress-slider').val(curTime/totalTime);
    });

    socket.on('queue_change', function(queue_data) {
        queued_songs = JSON.parse(queue_data);
        reloadQueue(queued_songs);
        var newQueuedSong = createQueueItem(currentSong, currentEndTime, true);
        list.prepend(newQueuedSong);
    });
    
    function updateClient(state) {
        var jsonState = JSON.parse(state);
        if (jsonState != null)
        {
            console.log(jsonState);
            $('#volume-slider').val(jsonState.volume.toString());
            clearInterval(currentProgressInterval);

            if(jsonState.media != null){
                currentSong = jsonState.current_track
                currentTime = jsonState.current_time;
                currentEndTime = jsonState.duration;
                $('#progress-slider').val(currentTime/currentEndTime);
                if (jsonState.queue != null){
                    reloadQueue(JSON.parse(jsonState.queue));
                    var newQueuedSong = createQueueItem(currentSong, currentEndTime, true);
                    list.prepend(newQueuedSong);
                }
            }else{
                currentSong = null;
                currentTime = 0;
                currentEndTime = 0;
                $('#progress-slider').val(0);
                $('#title').text("ACM Concert");
                list.empty()
            }

            if(jsonState.media != null && jsonState.is_playing == true){
                currentUrl = jsonState.media;
                var title = jsonState.current_track;
                $('#title').text(title);
                $('.playing .track').text(title);
                if(jsonState.audio_status != "State.Paused"){
                    currentProgressInterval = setInterval(updateProgress, 1000);
                }
            } else{
                currentUrl = null;
                $('#title').text("ACM Concert");
                list.empty()
            }
    
            if (jsonState.is_playing && (jsonState.audio_status == "State.Playing" || jsonState.audio_status == "State.Opening")) {
                $('#play-pause-button').removeClass('fa-play').addClass('fa-pause');
            } else{
                $('#play-pause-button').addClass('fa-play').removeClass('fa-pause');
            }
        }
    }
});
