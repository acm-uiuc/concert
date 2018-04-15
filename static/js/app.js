audioState = {
    song: null,
    time: 0,
    endTime: 0,
    progressInterval: null,
    playedby: null
};
windowUI = {
    body: $('body'),
    loginBtn: $('#submit-btn'),
    importBtn: $('#import-btn'),
    searchBox: $('#url-textbox'),
    spinner: $('.spinner')
};
playerUI = {
    thumbnail: null,
    playerMain: $('#main'),
    playerTitle: $('#title'),
    playBtn: $('#play-pause-button'),
    nextBtn: $('#next'),
    progressBar: $('#progress-slider'),
    playerContent: $('#player-content'),
    clearBtn: $('#clear')
};
var loginModal = $('#login-modal');
var queue = $('#playlist');

// Setup queue menu button
$('.menu').click(function() {
  playerUI.playerContent.toggleClass('show');
  playerUI.clearBtn.toggleClass('clear-queue-hidden');
});

/* Document key detection */
$(document).keyup(function(e) {
    if (e.keyCode == 13) {
        if (loginModal.css('display') == "block") {
            windowUI.loginBtn.click();
        } else {
            if (!searchJustActive || userJustClicked) {
                windowUI.importBtn.click();
            } else {
                searchJustActive = false;
            }
        }
    }
    if (e.keyCode == 27) {
        if (loginModal.css('display') == "block") {
            loginModal.css('display', "none");
        }
    }
    if (e.keyCode == 32 && !searchCurrentlyActive) {
        socket.emit('pause');
    }
    userJustClicked = false;
});

/* Login Functions */
windowUI.loginBtn.click(function () {
    var username = $('#uname-input').val();
    var password = $('#password-input').val();
    var data = {"username": username, "password": password};

    windowUI.loginBtn.css("display", "none");
    windowUI.spinner.css("display", "block");
    windowUI.loginBtn.prop('disabled', 'true');

    $.ajax({
        url: '/login',
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json",
      }).done(function (response) {
        window.location.replace("/");
      }).fail(function (response) {
        alert(response.responseText);
        windowUI.loginBtn.html('Login');
        windowUI.loginBtn.css("display", "block");
        windowUI.spinner.css("display", "none");
        windowUI.loginBtn.css('width', '80px');
        windowUI.loginBtn.removeAttr("disabled");
      });
});

/* Queue Functions */
function createQueueItem(title, time, mid, playedby, songPlaying) {
    time = formatSeconds(time/1000);

    var entry = document.createElement('li');
    if (songPlaying) {
        entry.className += "playing";
    } else {
        entry.className += "playlist-item";
        entry.setAttribute("onclick", "playlistAction(this)");
    }
    entry.setAttribute("onmouseover", "viewWhoPlayed(this)");
    entry.setAttribute("onmouseout", "hideWhoPlayed(this)");
    entry.dataset.title = title;
    entry.dataset.songId = mid;
    entry.dataset.time = time;
    entry.dataset.playedby = playedby;

    var content = document.createElement('a');
    content.className += "track";
    content.innerText = title;

    var timeInfo = document.createElement('span');
    timeInfo.className += "time";
    timeInfo.innerText = time;

    var playlistClearSpan = document.createElement('span');
    playlistClearSpan.style.display = "none";
    playlistClearSpan.className += "time";
    var itemClearBtn = document.createElement('i');
    itemClearBtn.className += "fa fa-times item-clear";
    playlistClearSpan.appendChild(itemClearBtn);

    entry.appendChild(content);
    entry.appendChild(timeInfo);
    entry.appendChild(playlistClearSpan);
    return entry;
}

function reloadQueue(serverQueue){
    if (audioState.song != null) {
        var firstSong = createQueueItem(audioState.song, audioState.endTime, null, audioState.playedby, true);
        var len = serverQueue.length;
        queue.empty();
        queue.append(firstSong);
        for(var i = 0; i < len; i++){
            var curSong = serverQueue[i];
            var newQueuedSong = createQueueItem(curSong.title, curSong.duration, curSong.mid, curSong.playedby, false);
            queue.append(newQueuedSong);
        }
    }
}

function viewWhoPlayed(obj) {
    var titleHolder = $($(obj).children()[0]);
    titleHolder.text(obj.dataset.playedby);
}

function hideWhoPlayed(obj) {
    var titleHolder = $($(obj).children()[0]);
    titleHolder.text(obj.dataset.title);
}

function playlistAction(obj) {
    //var timeHolder = $($(obj).children()[1]);
    //var clearHolder = $($(obj).children()[2]);
    //timeHolder.toggle();
    //clearHolder.toggle();
    if (confirm("Clear From Queue?")) {
        socket.emit('c_remove_song', obj.dataset.songId);
    }
}

/* UI Functions */
function toggleDarkMode(on) {
    if (on) {
        $('.title-text').removeClass('light');
        $('.title-text').addClass('dark');
        $('.button').removeClass('light');
        $('.button').addClass('dark'); 
        $('#url-textbox').removeClass('light');
        $('#url-textbox').addClass('dark'); 
        $('#import-btn').removeClass('light');
        $('#import-btn').addClass('dark');     
        $("#acm-logo").attr("src", "static/images/acm-logo-inverted.png"); 
    } else {
        $('.title-text').addClass('light');
        $('.title-text').removeClass('dark');
        $('.button').addClass('light');
        $('.button').removeClass('dark');
        $('#url-textbox').removeClass('dark');
        $('#url-textbox').addClass('light'); 
        $('#import-btn').removeClass('dark');
        $('#import-btn').addClass('light');  
        $("#acm-logo").attr("src", "static/images/acm-logo.png"); 
    }
}

function setDynamicBackground() {
    var image = new Image;
    image.src = playerUI.thumbnail;
    image.onload = function() {
        var colorThief = new ColorThief();
        var paletteArray = colorThief.getPalette(image, 2);
        var dominantColor = paletteArray[0];
        var rbgVal = `rgb(${dominantColor[0]}, ${dominantColor[1]}, ${dominantColor[2]})`;
        console.log(rbgVal);
        windowUI.body.css('background-color', rbgVal);
        var brightness = RGBtoHSV(dominantColor[0], dominantColor[1], dominantColor[2])['v'];
        if (brightness < 0.6) {
            toggleDarkMode(true);
        } else {
            toggleDarkMode(false);
        }
    }
}

window.onclick = function(event) {
    if (event.target == loginModal) {
        loginModal.style.display = "none";
    }
}

function updateProgress() {
    audioState.time += 1000;
    playerUI.progressBar.val(audioState.time / audioState.endTime);
}

/* Updates overall state of the Player, Queue, and Window */
function updateClient(serverState) {
    if (serverState == null) {
        return;
    }

    console.log(serverState);

    // Update Volume State
    player.volume = serverState.player.volume / 100;
    updateVolume();

    // Reset Song Progress Bar
    clearInterval(audioState.progressInterval);

    // Update Audio, playerUI, and Queue State
    if(serverState.player.is_playing == true) {
        audioState.song = serverState.player.current_track_info.title;
        audioState.time = serverState.player.current_track_info.current_time;
        audioState.endTime = serverState.player.current_track_info.duration;
        audioState.playedby = serverState.player.current_track_info.playedby
        if(serverState.player.audio_status != "State.Paused"){
            audioState.progressInterval = setInterval(updateProgress, 1000);
        }

        if (playerUI.thumbnail != serverState.player.current_track_info.thumbnail_url) {
            playerUI.thumbnail = serverState.player.current_track_info.thumbnail_url;
            playerUI.playerMain.css("background-image", `url(${playerUI.thumbnail})`);  
            playerUI.playerMain.css("background-size", "cover"); 
            setDynamicBackground();
        }
        playerUI.progressBar.val(audioState.time/audioState.endTime);
        playerUI.playerTitle.text(serverState.player.current_track_info.title);

        if (serverState.queue != null){
            reloadQueue(serverState.queue);
        }
    } else {
        audioState.song = null;
        audioState.time = 0;
        audioState.endTime = 0;
        audioState.playedby = null;
        playerUI.thumbnail = null;
        playerUI.playerMain.css("background-image", "url(static/images/acm-logo.png)"); 
        playerUI.playerMain.css("background-size", "100%"); 
        playerUI.progressBar.val(0);
        playerUI.playerTitle.text("ACM Concert");
        windowUI.body.css('background-color', 'rgba(34, 34, 34, 0.1)');
        toggleDarkMode(false);
        queue.empty();
    }

    // Toggle play/pause button
    if (serverState.player.is_playing && (serverState.player.audio_status == "State.Playing" || serverState.player.audio_status == "State.Opening")) {
        playerUI.playBtn.removeClass('fa-play').addClass('fa-pause');
    } else {
        playerUI.playBtn.addClass('fa-play').removeClass('fa-pause');
    }
}