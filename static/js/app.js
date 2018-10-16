const audioState = {
    song: null,
    id: null,
    time: 0,
    endTime: 0,
    progressInterval: null,
    playedby: null
};

const windowUI = {
    body: $('body'),
    loginBtn: $('#submit-btn'),
    importBtn: $('#import-btn'),
    searchBox: $('#url-textbox'),
    spinner: $('.spinner'),
    acmLogo: $('#acm-logo'),
    titleText: $('.title-text'),
    button: $('.button'),
    searchBar: $(".select2-container"),
    searchText: $(".select2-search__field"),
    playlist: $(".playlist"),
    bgColor: null,
    fgColor: null,
    otherStyles: null
};

const playerUI = {
    thumbnail: null,
    playerMain: $('#main'),
    playerTitle: $('#title'),
    playBtn: $('#play-pause-button'),
    nextBtn: $('#next'),
    progressBar: $('#progress-slider'),
    playerContent: $('#player-content'),
    clearBtn: $('#clear')
};

const loginModal = $('#login-modal');
const queue = $('#playlist');


/* Setup Desktop Notifcations */
document.addEventListener('DOMContentLoaded', () => {
    if (!Notification) {
        alert('Desktop notifications not available in your browser. Try Firefox.');
    } else if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
});

function notifyPlayed() {
    if (Notification.permission !== "granted")
        Notification.requestPermission();
    else {
        const notification = new Notification(`Now Playing ${audioState.song}`, {
            icon: playerUI.thumbnail,
            body: `Queued by ${audioState.playedby}`,
        });
        notification.onshow = (event) => {
            setTimeout(notification.close, 3000);
        }
    }
}

// Setup queue menu button
$('.menu').click(() => {
    playerUI.playerContent.toggleClass('show');
    playerUI.clearBtn.toggleClass('clear-queue-hidden');
});

$(document).ready(() => {
    const sheet = document.createElement('style');
    document.head.appendChild(sheet);
    windowUI.otherStyles = sheet.sheet;
});

/* Document key detection */
$(document).keyup((event) => {
    const keyCodeIs13 = event.keyCode == 13;
    
    if (keyCodeIs13 && loginModal.css('display') == "block") {
        windowUI.loginBtn.click();
    } else if (keyCodeIs13 && (!searchJustActive || userJustClicked)) {
        windowUI.importBtn.click();
    } else if (keyCodeIs13) {
        searchJustActive = false;
    } else if (event.keyCode == 27 && loginModal.css('display') == "block") {
        loginModal.css('display', "none");
    } else if (event.keyCode == 32 && !searchCurrentlyActive) {
        socket.emit('c_pause');
    }

    userJustClicked = false;
});

/* Login Functions */
windowUI.loginBtn.click(() => {
    const username = $('#uname-input').val();
    const password = $('#password-input').val();

    windowUI.loginBtn.css("display", "none");
    windowUI.spinner.css("display", "block");
    windowUI.loginBtn.prop('disabled', 'true');

    $.ajax({
        url: '/login',
        type: "POST",
        data: JSON.stringify({username, password}),
        contentType: "application/json",
    }).done((response) => {
        window.location.replace("/");
    }).fail((response) => {
        alert(response.responseText);
        windowUI.loginBtn.html('Login');
        windowUI.loginBtn.css("display", "block");
        windowUI.spinner.css("display", "none");
        windowUI.loginBtn.css('width', '80px');
        windowUI.loginBtn.removeAttr("disabled");
    });
});

/* Queue Functions */
function createQueueItem(title, time, id, playedby, songPlaying) {
    time = formatSeconds(time / 1000);

    let entry = document.createElement('li');

    if (songPlaying) {
        entry.className += "playing";
    } else {
        entry.className += "playlist-item";
        entry.setAttribute("onclick", "playlistAction(this)");
    }

    entry.setAttribute("onmouseover", "showTrackAttribute(this, 'playedby')");
    entry.setAttribute("onmouseout", "showTrackAttribute(this, 'title')");

    entry.dataset.title = title;
    entry.dataset.id = id;
    entry.dataset.time = time;
    entry.dataset.playedby = playedby;

    const content = document.createElement('a');
    content.className += "track";
    content.innerText = title;

    const timeInfo = document.createElement('span');
    timeInfo.className += "time";
    timeInfo.innerText = time;

    const playlistClearSpan = document.createElement('span');
    playlistClearSpan.style.display = "none";
    playlistClearSpan.className += "time";

    const itemClearBtn = document.createElement('i');
    itemClearBtn.className += "fa fa-times item-clear";

    playlistClearSpan.appendChild(itemClearBtn);

    entry.appendChild(content);
    entry.appendChild(timeInfo);
    entry.appendChild(playlistClearSpan);
    return entry;
}

function reloadQueue(serverQueue) {
    if (audioState.song == null) {
        return;
    }

    const firstSong = createQueueItem(audioState.song, audioState.endTime, audioState.id, audioState.playedby, true);

    queue.empty();
    queue.append(firstSong);

    for (let i = 0; i < serverQueue.length; i++) {
        const curSong = serverQueue[i];
        const newQueuedSong = createQueueItem(curSong.title, curSong.duration, curSong.id, curSong.playedby, false);
        queue.append(newQueuedSong);
    }
}

function showTrackAttribute(obj, attr) {
    const titleHolder = $($(obj).children()[0]);
    titleHolder.text(obj.dataset[attr]);
}

function playlistAction(obj) {
    if (confirm("Clear From Queue?")) {
        socket.emit('c_remove_song', obj.dataset.id);
    }
}

function get_handlers() {
    windowUI.searchBar = $(".select2-container");
    windowUI.searchText = $(".select2-search__field");
    windowUI.search_selection = $(".select2-selection__choice");
}

function color_style(button_color, bgColor) {
    windowUI.body.css('background-color', bgColor);
    windowUI.acmLogo.css("fill", button_color);
    windowUI.titleText.css('color', button_color);
    windowUI.button.css('background-color', button_color);
    windowUI.button.css('color', bgColor);
    windowUI.importBtn.css("background-color", button_color);
    windowUI.importBtn.css("color", bgColor);
    windowUI.searchBar.attr('style', `border-bottom-color:${button_color}; color:${button_color};`);
    windowUI.searchText.attr('style', `width:58vw; color:${button_color};`);

    if (windowUI.otherStyles.cssRules.length > 0) {
        windowUI.otherStyles.deleteRule(1);
        windowUI.otherStyles.deleteRule(0);
    }

    windowUI.otherStyles.insertRule(`.select2-search__field::placeholder { color: ${button_color}; }`, 0);
    windowUI.otherStyles.insertRule(`.select2-selection__choice{ color: ${button_color} !important; }`, 1);
    windowUI.searchText.attr('style', `width:58vw; color:${button_color};`);
    windowUI.playlist.css('background-color', button_color);
    windowUI.playlist.css('color', bgColor);
}

function setDynamicBackground() {
    const image = new Image;
    image.src = playerUI.thumbnail;
    get_handlers();

    image.onload = () => {
        const colorThief = new ColorThief();
        const paletteArray = colorThief.getPalette(image, 2);
        const dominantColor = paletteArray[0];
        const otherColor = paletteArray[1];
        windowUI.bgColor = `rgb(${dominantColor[0]}, ${dominantColor[1]}, ${dominantColor[2]})`;
        windowUI.fgColor = `rgb(${otherColor[0]}, ${otherColor[1]}, ${otherColor[2]})`;
        color_style(windowUI.fgColor, windowUI.bgColor);
    }
}

window.onclick = (event) => {
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

    // Update Volume State
    player.volume = serverState.player.volume / 100;
    updateVolume();

    // Reset Song Progress Bar
    clearInterval(audioState.progressInterval);

    // Update Audio, playerUI, and Queue State
    if (serverState.player.is_playing == true) {
        audioState.song = serverState.player.current_track_info.title;
        audioState.id = serverState.player.current_track_info.id;
        audioState.time = serverState.player.current_track_info.current_time;
        audioState.endTime = serverState.player.current_track_info.duration;
        audioState.playedby = serverState.player.current_track_info.playedby

        if (serverState.player.audio_status != "State.Paused") {
            audioState.progressInterval = setInterval(updateProgress, 1000);
        }

        if (playerUI.thumbnail != serverState.player.current_track_info.thumbnail_url) {
            playerUI.thumbnail = serverState.player.current_track_info.thumbnail_url;
            playerUI.playerMain.css("background-image", `url(${playerUI.thumbnail})`);
            playerUI.playerMain.css("background-size", "cover");
        }

        setDynamicBackground();

        playerUI.progressBar.val(audioState.time / audioState.endTime);
        playerUI.playerTitle.text(serverState.player.current_track_info.title);

        if (serverState.queue != null) {
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
        windowUI.bgColor = 'rgb(255, 255, 255)';
        windowUI.fgColor = 'rgb(0, 0, 0)';

        color_style(windowUI.fgColor, windowUI.bgColor);
        
        queue.empty();
    }

    // Toggle play/pause button
    if (serverState.player.is_playing && (serverState.player.audio_status == "State.Playing" || serverState.player.audio_status == "State.Opening")) {
        playerUI.playBtn.removeClass('fa-play').addClass('fa-pause');
    } else {
        playerUI.playBtn.addClass('fa-play').removeClass('fa-pause');
    }
}

$('.trigger, .slider').click(() => {
    $('.slider').toggleClass('close');
});