var socket;
var urlProtocol = 'https://';

$(document).ready(function () {
    if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
        urlProtocol = 'http://';
    } 
    socket = io.connect(urlProtocol + document.domain + ':' + location.port);
    /* Socket Events */
    socket.on('s_connected', function(state) {
        serverState = JSON.parse(state);
        updateClient(serverState);
        console.log("Connected to Server");
    });

    socket.on('s_failed_queue', function() {
        console.log("Invalid URL");
    });

    socket.on('s_stopped', function(serverState) {
        serverState = JSON.parse(state);
        updateClient(serverState);
    });

    socket.on('s_played', function(state) {
        serverState = JSON.parse(state);
        updateClient(serverState);
        playerUI.playBtn.addClass('pause');
        playerUI.playBtn.removeClass('play');
        clearInterval(audioState.progressInterval);
        audioState.progressInterval = setInterval(updateProgress, 1000);
    });

    socket.on('s_heartbeat', function(state) {
        serverState = JSON.parse(state);
        updateClient(serverState);
        console.log("hrbt recieved");
    });

    socket.on('s_paused', function(state) {
        var playState = JSON.parse(state).player;
        console.log(playState);
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

    socket.on('s_skipped', function(state) {
        serverState = JSON.parse(state);
        updateClient(serverState);
    });

    socket.on('s_cleared', function(state) {
        serverState = JSON.parse(state);
        updateClient(serverState);
    });

    socket.on('s_volume_changed', function(volumeResponse) {
        volumeState = JSON.parse(volumeResponse);
        player.volume = volumeState.volume / 100;
        updateVolume();
    });

    socket.on('s_position_changed', function() {
        var curTime = jsonState.current_time;
        var totalTime = jsonState.duration;
        playerUI.progressBar.val(curTime/totalTime);
    });

    //Add, Remove, Clear, Response
    socket.on('s_queue_changed', function(serverState) {
        queueData = JSON.parse(serverState).queue;
        reloadQueue(queueData);
    });

    /* Play Controls */
    playerUI.playBtn.click(function(e) {
        socket.emit('c_pause');
    });

    playerUI.nextBtn.click(function(e) { 
        if (loggedin) {
            socket.emit('c_skip');
        } else {
            alert("Please login to skip this song");
        }
    });

    playerUI.clearBtn.click(function() {
        socket.emit('c_clear');
    });

    windowUI.importBtn.click(function(e) {
        var inputVal = $('.select2-selection__choice').text();
        if (inputVal.trim() != ""){
            var currentUrl = inputVal.replace(/[^\x00-\x7F]/g, "");
            if (loggedin) {
                if (!isURL(currentUrl) || (!currentUrl.includes("youtube.com") && !currentUrl.includes("soundcloud.com"))) {
                    alert("Please enter a valid url");
                } else {
                    socket.emit('c_queue_song', currentUrl);
                }
            } else {
                alert("Please login to add to queue");
            }
            $("#url-textbox").val(null).trigger('change');
        }
    });

    socket.emit("c_connected");
});