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
    searchBox: $('#url-textbox')
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

/* Setup Desktop Notifcations */
document.addEventListener('DOMContentLoaded', function () {
  if (!Notification) {
    alert('Desktop notifications not available in your browser. Try Chromium.'); 
    return;
  }
  if (Notification.permission !== "granted") {
    Notification.requestPermission();
  }
});

function notifyPlayed(thumbnail, songTitle) {
    if (Notification.permission !== "granted")
        Notification.requestPermission();
    else {
        var notification = new Notification('Now Playing', {
          icon: thumbnail,
          body: songTitle,
        });
        notification.onshow = function(event) { 
            setTimeout(function() { notification.close(); }, 3000);
            cancelReminders(event); 
        }
    }
}

/* Setup queue menu button */
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

    windowUI.loginBtn.html('Logging In...');
    windowUI.loginBtn.css('width', '100px');
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
        entry.setAttribute("onclick", "clearSingleSong(this)");
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

function reloadQueue(queueData){
    if (audioState.song != null) {
        var firstSong = createQueueItem(audioState.song, audioState.endTime, null, audioState.playedby, true);
        var queued_songs = JSON.parse(queueData);
        var len = queued_songs.length;
        queue.empty();
        queue.append(firstSong);
        for(var i = 0; i < len; i++){
            var curSong = queued_songs[i];
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

function clearSingleSong(obj) {
    if (confirm("Clear From Queue?")) {
        socket.emit('remove_song', obj.dataset.songId);
    }
}

/* UI Functions */
function toggleDarkMode(on) {
    if (on) {
        $('.title-text').removeClass('light');
        $('.title-text').addClass('dark');
        $('.button').removeClass('light');
        $('.button').addClass('dark');    
        $("#acm-logo").attr("src", "static/images/acm-logo-inverted.png"); 
    } else {
        $('.title-text').addClass('light');
        $('.title-text').removeClass('dark');
        $('.button').addClass('light');
        $('.button').removeClass('dark');
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
        var rbgVal = "rgb({0}, {1}, {2})".format(dominantColor[0], dominantColor[1], dominantColor[2]);
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
function updateClient(state) {
    if (state == null) return;
    var jsonState = JSON.parse(state);

    // Update Volume State
    player.volume = jsonState.volume / 100;
    updateVolume();

    // Reset Song Progress Bar
    clearInterval(audioState.progressInterval);

    // Update Audio, playerUI, and Queue State
    if(jsonState.media != null){
        audioState.song = jsonState.current_track
        audioState.time = jsonState.current_time;
        audioState.endTime = jsonState.duration;
        audioState.playedby = jsonState.playedby
        if(jsonState.audio_status != "State.Paused"){
            audioState.progressInterval = setInterval(updateProgress, 1000);
        }

        if (playerUI.thumbnail != jsonState.thumbnail) {
            playerUI.thumbnail = jsonState.thumbnail;
            playerUI.playerMain.css("background-image", "url({0})".format(playerUI.thumbnail));  
            playerUI.playerMain.css("background-size", "cover"); 
            setDynamicBackground();
        }
        playerUI.progressBar.val(audioState.time/audioState.endTime);
        playerUI.playerTitle.text(jsonState.current_track);

        if (jsonState.queue != null){
            reloadQueue(jsonState.queue);
        }
    }else{
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
    if (jsonState.is_playing && (jsonState.audio_status == "State.Playing" || jsonState.audio_status == "State.Opening")) {
        playerUI.playBtn.removeClass('fa-play').addClass('fa-pause');
    } else{
        playerUI.playBtn.addClass('fa-play').removeClass('fa-pause');
    }
}