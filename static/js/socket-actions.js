let socket;

$(document).ready(() => {
    const urlProtocol = (location.hostname === "localhost" || location.hostname === "127.0.0.1") ?
        'http://' :
        'https://';

    socket = io.connect(urlProtocol + document.domain + ':' + location.port);

    socket.on('s_connected', (state) => {
        updateClient(JSON.parse(state));
        console.log("Connected to Server");
    });

    socket.on('s_failed_queue', () => {
        console.log("Invalid URL");
    });

    socket.on('s_stop', updateClientWithState);

    socket.on('s_play', (state) => {
        updateClient(JSON.parse(state));

        playerUI.playBtn.addClass('pause');
        playerUI.playBtn.removeClass('play');

        clearInterval(audioState.progressInterval);

        audioState.progressInterval = setInterval(updateProgress, 1000);
        notifyPlayed();
    });

    socket.on('s_heartbeat', (state) => {
        updateClient(JSON.parse(state));
        console.log("hrbt recieved");
    });

    socket.on('s_artwork_available', (state) => {
        updateClient(JSON.parse(state));
        console.log("new artwork recieved");
    });

    socket.on('s_pause', (state) => {
        const playState = JSON.parse(state).player;
        console.log(playState);
        if (playState.is_playing && (playState.audio_status == "State.Playing" || playState.audio_status == "State.Opening")) {
            audioState.progressInterval = setInterval(updateProgress, 1000);
            playerUI.playBtn.removeClass('fa-play').addClass('fa-pause');
        } else {
            clearInterval(audioState.progressInterval);
            playerUI.playBtn.addClass('fa-play').removeClass('fa-pause');
        }

        audioState.time = playState.current_time;
        audioState.endTime = playState.duration;
    });

    socket.on('s_skipped', updateClientWithState);

    socket.on('s_cleared', updateClientWithState);

    socket.on('s_volume_changed', (volumeResponse) => {
        const volumeState = JSON.parse(volumeResponse);
        player.volume = volumeState.volume / 100;
        updateVolume();
    });

    socket.on('s_position_changed', () => {
        const curTime = jsonState.current_time;
        const totalTime = jsonState.duration;
        playerUI.progressBar.val(curTime / totalTime);
    });

    //Add, Remove, Clear, Response
    socket.on('s_queue_changed', (serverState) => {
        reloadQueue(JSON.parse(serverState).queue);
    });

    /* Play Controls */
    playerUI.playBtn.click((e) => {
        socket.emit('c_pause');
    });

    playerUI.nextBtn.click((e) => {
        if (isUserLoggedIn) {
            socket.emit('c_skip');
        } else {
            alert("Please login to skip this song");
        }
    });

    playerUI.clearBtn.click(() => {
        socket.emit('c_clear');
    });

    windowUI.importBtn.click((e) => {
        const inputVal = $('.select2-selection__choice').text() || $('.select2-search__field').val();

        if (inputVal.trim() == "") {
            return;
        }

        const currentUrl = inputVal.replace(/[^\x00-\x7F]/g, "");

        if (isUserLoggedIn) {
            if (!isURL(currentUrl) || (!currentUrl.includes("youtube.com") && !currentUrl.includes("soundcloud.com"))) {
                alert("Please enter a valid url");
            } else {
                socket.emit('c_queue_song', currentUrl);
            }
        } else {
            alert("Please login to add to queue");
        }

        $("#url-textbox").val(null).trigger('change');
    });

    socket.emit("c_connected");
});

function updateClientWithState(state) {
    updateClient(JSON.parse(state));
}