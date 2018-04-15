var socket;
var urlProtocol = 'https://';

$(document).ready(function () {
    if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
        urlProtocol = 'http://';
    } 
    socket = io.connect(urlProtocol + document.domain + ':' + location.port);

    /* Socket Events */
    socket.on('connected', function(state) {
        updateClient(state);
    });

    socket.on('download_error', function() {
        console.log("Invalid URL");
    });

    socket.on('stopped', function(state) {
        updateClient(state);
    });

    socket.on('played', function(state) {
        updateClient(state);
        playerUI.playBtn.addClass('pause');
        playerUI.playBtn.removeClass('play');
        clearInterval(audioState.progressInterval);
        audioState.progressInterval = setInterval(updateProgress, 1000);
    });

    socket.on('heartbeat', function(state) {
        updateClient(state);
    });

    socket.on('paused', function(state) {
        var playState = JSON.parse(state);
        if (playState.is_playing && (playState.audio_status == "State.Playing" || playState.audio_status == "State.Opening")){
            audioState.progressInterval = setInterval(updateProgress, 1000); 
            playerUI.playBtn.removeClass('fa-play').addClass('fa-pause');
        }
        else{
            clearInterval(audioState.progressInterval);
            playerUI.playBtn.addClass('fa-play').removeClass('fa-pause');
        }
        audioState.time = playState.current_time;
        audioState.endTime = playState.duration;
    });

    socket.on('skipped', function(state) {
        updateClient(state);
    });

    socket.on('cleared', function(queueData) {
        reloadQueue(queueData);
    });

    socket.on('removed', function(queueData) {
        reloadQueue(queueData);
    });

    socket.on('volume_changed', function(volumeResponse) {
        volumeState = JSON.parse(volumeResponse);
        player.volume = volumeState.volume / 100;
        updateVolume();
    });

    socket.on('position_changed', function() {
        var curTime = jsonState.current_time;
        var totalTime = jsonState.duration;
        playerUI.progressBar.val(curTime/totalTime);
    });

    socket.on('queue_change', function(queueData) {
        reloadQueue(JSON.parse(queueData));
    });

    /* Play Controls */
    playerUI.playBtn.click(function(e) {
        socket.emit('pause');
    });

    playerUI.nextBtn.click(function(e) { 
        if (loggedin) {
            socket.emit('skip');
        } else {
            alert("Please login to skip this song");
        }
    });

    playerUI.clearBtn.click(function() {
        socket.emit('clear');
    });

    windowUI.importBtn.click(function(e) {
        var inputVal = $('.select2-selection__choice').text();
        if (inputVal.trim() != ""){
            var currentUrl = inputVal.replace(/[^\x00-\x7F]/g, "");
            if (loggedin) {
                if (!isURL(currentUrl) || (!currentUrl.includes("youtube.com") && !currentUrl.includes("soundcloud.com"))) {
                    alert("Please enter a valid url");
                } else {
                    socket.emit('download', currentUrl);
                }
            } else {
                alert("Please login to add to queue");
            }
            windowUI.searchBox.val(null).trigger('change');
        }
    });
});