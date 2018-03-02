var socket;
var currentSong;
var currentTime;
var currentEndTime;
var currentProgressInterval;
var currentThumbnail;
var list = $('#playlist');

//Setup Playlist Menu
$('.menu').click(function() {
  $('#player').toggleClass('show');
});


var modal = document.getElementById('login-form');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

//Helper Functions
function getThumbnailPath(mrl) {
    var parts = mrl.split("/");
    var filePath =  parts[parts.length - 1];
    var prefix = filePath.split('.')[0];
    return "static/thumbnails/" + prefix + ".jpg";
}

if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

function formatSeconds(time) {
    var minutes = Math.floor(time / 60);
    var seconds = time - minutes * 60;
    return str_pad_left(minutes,'0',2)+':'+str_pad_left(seconds,'0',2);
}

function str_pad_left(string,pad,length) {
    return (new Array(length+1).join(pad)+string).slice(-length);
}

function updateProgress() {
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

//Socket Functions
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

    $("#import-btn").click(function(e) {
        if ($('#url-textbox').val().trim() != ""){
            var currentUrl = $('#url-textbox').val();
            socket.emit('download', currentUrl);
            $('#url-textbox').val("");
        }
        else{
            return false;
        }
    });

    socket.on('downloaded', function(state) {
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
            // Update Volume State
            player.volume = jsonState.volume / 100;
            updateVolume();

            // Reset Song Progress Bar
            clearInterval(currentProgressInterval);

            // Update Track and Queue State
            if(jsonState.media != null){
                currentSong = jsonState.current_track
                currentTime = jsonState.current_time;
                currentEndTime = jsonState.duration;
                if (currentThumbnail != jsonState.thumbnail) {
                    currentThumbnail = getThumbnailPath(jsonState.media);
                    $('#main').css("background-image", "url({0})".format(currentThumbnail));  
                    var image = new Image;
                    image.src = currentThumbnail;
                    image.onload = function() {
                        var colorThief = new ColorThief();
                        var paletteArray = colorThief.getPalette(image, 2);
                        var dominantColor = paletteArray[0];
                        var rbgVal = "rgb({0}, {1}, {2})".format(dominantColor[0], dominantColor[1], dominantColor[2]);
                        $('body').css('background-color', rbgVal);
                    }
                }
                $('#progress-slider').val(currentTime/currentEndTime);

                var title = jsonState.current_track;
                $('#title').text(title);
                $('.playing .track').text(title);
                if(jsonState.audio_status != "State.Paused"){
                    currentProgressInterval = setInterval(updateProgress, 1000);
                }

                if (jsonState.queue != null){
                    reloadQueue(JSON.parse(jsonState.queue));
                    var newQueuedSong = createQueueItem(currentSong, currentEndTime, true);
                    list.prepend(newQueuedSong);
                }
            }else{
                currentSong = null;
                currentTime = 0;
                currentEndTime = 0;
                currentThumbnail = null;
                $('body').css('background-color', 'rgba(34, 34, 34, 0.1)');
                $('#main').css("background-image", "none");  
                $('#progress-slider').val(0);
                $('#title').text("ACM Concert");
                list.empty()
            }
    
            // Toggle play/pause button
            if (jsonState.is_playing && (jsonState.audio_status == "State.Playing" || jsonState.audio_status == "State.Opening")) {
                $('#play-pause-button').removeClass('fa-play').addClass('fa-pause');
            } else{
                $('#play-pause-button').addClass('fa-play').removeClass('fa-pause');
            }
        }
    }
});
