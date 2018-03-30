var socket;
var currentSong = null;
var currentTime;
var currentEndTime;
var currentProgressInterval;
var currentThumbnail;
var modal = document.getElementById('login-modal');
var list = $('#playlist');
var submitBtn = $('#submit-btn');

// Setup Playlist Menu
$('.menu').click(function() {
  $('#player').toggleClass('show');
  $('.clear-queue').toggleClass('clear-queue-hidden');
});

// Handle Login
$(document).keyup(function(e) {
    if (e.keyCode == 13) {
        if ($('#login-modal').css('display') == "block") {
            submitBtn.click();
        } else {
            $('#import-btn').click();
        }
    }
    if (e.keyCode == 27) {
        if (modal.style.display == "block") {
            modal.style.display = "none";
        }
    }
});

submitBtn.click(function () {
    var username = $('#uname-input').val();
    var password = $('#password-input').val();
    var data = {"username": username, "password": password};

    submitBtn.html('Logging In...');
    submitBtn.css('width', '100px');
    submitBtn.prop('disabled', 'true');

    $.ajax({
        url: '/login',
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json",
      }).done(function (response) {
        window.location.replace("/");
      }).fail(function (response) {
        alert(response.responseText);
        submitBtn.html('Login');
        submitBtn.css('width', '80px');
        submitBtn.removeAttr("disabled");
      });
});

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

function isURL(str) {
  var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
  '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|'+ // domain name
  '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
  '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
  '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
  '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
  return pattern.test(str);
}

function updateProgress() {
    currentTime += 1000;
    $('#progress-slider').val(currentTime/currentEndTime);
}

function createQueueItem(title, time, songPlaying, callback) {
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
    if (callback) {
        callback(entry);
    } else {
        return entry;
    }
}

function reloadQueue(queue_data){
    if (currentSong != null) {
        createQueueItem(currentSong, currentEndTime, true, function(firstSong) {
            queued_songs = JSON.parse(queue_data);
            var len = queued_songs.length;
            list.empty();
            list.append(firstSong);
            for(var i = 0; i < len; i++){
                var curSong = queued_songs[i];
                var newQueuedSong = createQueueItem(curSong.title, curSong.duration, false, null);
                list.append(newQueuedSong);
            }
        });
    }
}

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

//Socket Functions
$(document).ready(function () {
    if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
        socket = io.connect('http://' + document.domain + ':' + location.port);
    } else {
        socket = io.connect('https://' + document.domain + ':' + location.port);
    }
    socket.on('connected', function(state) {
        updateClient(state);
    });

    $('#play-pause-button').click(function(e) {
        socket.emit('pause');
    });

    $('#next').click(function(e) { 
        if (loggedin) {
            socket.emit('skip');
        } else {
            alert("Please login to skip this song");
        }
    });

    $('#previous-button').click(function(e) { 
        socket.emit('previous');
    });

    $("#import-btn").click(function(e) {
        if ($('#url-textbox').val().trim() != ""){
            var currentUrl = $('#url-textbox').val();
            if (loggedin) {
                if (!isURL(currentUrl) || !currentUrl.includes("youtube.com")) {
                    alert("Please enter a valid url");
                } else {
                    socket.emit('download', currentUrl);
                }
            } else {
                alert("Please login to add to queue");
            }
            $('#url-textbox').val("");
        }
    });

    $('.clear-queue').click(function() {
        socket.emit('clear');
    });

    socket.on('download_error', function() {
        //TODO: Better error handling
        console.log("Invalid URL");
    });

    socket.on('stopped', function(state) {
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
        updateClient(state);
    });

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

    socket.on('cleared', function(queue_data) {
        reloadQueue(queue_data);
    });

    socket.on('volume_changed', function(volumeResponse) {
        volumeState = JSON.parse(volumeResponse);
        player.volume = volumeState.volume / 100;
        updateVolume();
    });

    socket.on('position_changed', function() {
        var curTime = jsonState.current_time;
        var totalTime = jsonState.duration;
        $('#progress-slider').val(curTime/totalTime);
    });

    socket.on('queue_change', function(queue_data) {
        reloadQueue(queue_data);
    });
    
    function updateClient(state) {
        if (state == null) return;
        var jsonState = JSON.parse(state);

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
                currentThumbnail = jsonState.thumbnail;
                $('#main').css("background-image", "url({0})".format(currentThumbnail));  
                $('#main').css("background-size", "cover"); 
                var image = new Image;
                image.src = currentThumbnail;
                image.onload = function() {
                    var colorThief = new ColorThief();
                    var paletteArray = colorThief.getPalette(image, 2);
                    var dominantColor = paletteArray[0];
                    var rbgVal = "rgb({0}, {1}, {2})".format(dominantColor[0], dominantColor[1], dominantColor[2]);
                    $('body').css('background-color', rbgVal);
                    var brightness = RGBtoHSV(dominantColor[0], dominantColor[1], dominantColor[2])['v'];
                    if (brightness < 0.6) {
                        toggleDarkMode(true);
                    } else {
                        toggleDarkMode(false);
                    }
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
                reloadQueue(jsonState.queue);
            }
        }else{
            currentSong = null;
            currentTime = 0;
            currentEndTime = 0;
            currentThumbnail = null;
            $('body').css('background-color', 'rgba(34, 34, 34, 0.1)');
            $('#main').css("background-image", "url(static/images/acm-logo.png)"); 
            $('#main').css("background-size", "100%"); 
            toggleDarkMode(false);
            $('#progress-slider').val(0);
            $('#title').text("ACM Concert");
            list.empty();
        }

        // Toggle play/pause button
        if (jsonState.is_playing && (jsonState.audio_status == "State.Playing" || jsonState.audio_status == "State.Opening")) {
            $('#play-pause-button').removeClass('fa-play').addClass('fa-pause');
        } else{
            $('#play-pause-button').addClass('fa-play').removeClass('fa-pause');
        }
    }
});
