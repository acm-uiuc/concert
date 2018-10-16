let currentlyDragged = null;
var volumeProgress = document.querySelector('.slider .progress');
var audioPlayer = document.querySelector('.audio-player');
var player = audioPlayer.querySelector('audio');

window.addEventListener('mousedown', (event) => {
    if (!isDraggable(event.target)) {
        return false;
    }

    currentlyDragged = event.target;
    const handleMethod = currentlyDragged.dataset.method;

    this.addEventListener('mousemove', window[handleMethod], false);

    window.addEventListener('mouseup', () => {
        currentlyDragged = false;
        window.removeEventListener('mousemove', window[handleMethod], false);
    }, false);
});

function isDraggable(el) {
    let canDrag = false;
    const elClasses = Array.from(el.classList);
    const draggableClasses = ['pin'];

    draggableClasses.forEach((draggable) => {
        if (elClasses.indexOf(draggable) !== -1) {
            canDrag = true
        };
    });

    return canDrag;
}

function inRange(event) {
    const rangeBox = getRangeBox(event);

    if (rangeBox.dataset.direction == 'horizontal') {
        const min = rangeBox.offsetLeft;
        const max = min + rangeBox.offsetWidth;

        if (event.clientX < min || event.clientX > max) {
            return false;
        }
    } else {
        const min = rangeBox.getBoundingClientRect().top;
        const max = min + rangeBox.offsetHeight;

        if (event.clientY < min || event.clientY > max) {
            return false;
        }
    }

    return true;
}

function getRangeBox(event) {
    if (event.type == 'click' && isDraggable(event.target)) {
        return event.target.parentElement.parentElement;
    }

    if (event.type == 'mousemove') {
        return currentlyDragged.parentElement.parentElement;
    }

    return event.target;
}

function getCoefficient(event) {
    const slider = getRangeBox(event);

    if (slider.dataset.direction == 'horizontal') {
        const offsetX = event.clientX - slider.offsetLeft;
        return offsetX / slider.clientWidth;
    }

    if (slider.dataset.direction == 'vertical') {
        var offsetY = event.clientY - slider.getBoundingClientRect().top;
        return 1 - offsetY / slider.clientHeight;
    }

    return 0;
}

function updateVolume() {
    volumeProgress.style.height = player.volume * 100 + '%';
    if (player.volume >= 0.5) {
        speaker.attributes.d.value = 'M14.667 0v2.747c3.853 1.146 6.666 4.72 6.666 8.946 0 4.227-2.813 7.787-6.666 8.934v2.76C20 22.173 24 17.4 24 11.693 24 5.987 20 1.213 14.667 0zM18 11.693c0-2.36-1.333-4.386-3.333-5.373v10.707c2-.947 3.333-2.987 3.333-5.334zm-18-4v8h5.333L12 22.36V1.027L5.333 7.693H0z';
    } else if (player.volume < 0.5 && player.volume > 0.05) {
        speaker.attributes.d.value = 'M0 7.667v8h5.333L12 22.333V1L5.333 7.667M17.333 11.373C17.333 9.013 16 6.987 14 6v10.707c2-.947 3.333-2.987 3.333-5.334z';
    } else if (player.volume <= 0.05) {
        speaker.attributes.d.value = 'M0 7.667v8h5.333L12 22.333V1L5.333 7.667';
    }
}

function changeVolume(event) {
    if (inRange(event)) {
        console.log("Previous: " + player.volume + ", Current: " + getCoefficient(event));
        player.volume = getCoefficient(event);
        updateVolume();
        socket.emit('c_volume', parseInt(player.volume * 100));
    }
}

$('.slider').on('change', changeVolume);

$('.volume-btn').click(function () {
    if (isUserLoggedIn) {
        $('.volume-controls').toggleClass('hidden');
        $('.volume-btn').toggleClass('open');
    }
});