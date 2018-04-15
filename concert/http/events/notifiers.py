import json
from concert.http.events import ConcertEventsSockets


############# STATUS UPDATE ######################

def notify_connected(state):
    _notify_on_channel("s_connected", state)

def notify_heartbeat(state):
    _notify_on_channel("s_heartbeat", state)

############# FAILURES ######################

def notify_failed_queue(state):
    _notify_on_channel("s_failed_queue", state)


def notify_failed_to_set_time(state):
    _notify_on_channel("s_failed_set_time", state)

############# CONFIRMATIONS ######################
def notify_song_queue(state):
    _notify_on_channel("s_song_queued", state)


def notify_paused(state):
    _notify_on_channel("s_paused", state)


def notify_new_song_playing(state):
    _notify_on_channel("s_played", state)


def notify_clear_queue(state):
    _notify_on_channel("s_cleared", state)


def notify_song_queued(state):
    _notify_on_channel("s_song_queued", state)


def notify_set_time(state):
    _notify_on_channel("s_set_time", state)


def notify_song_skip(state):
    _notify_on_channel("s_skipped", state)


def notify_no_song_playing(state):
    _notify_on_channel("s_stopped", state)

############# STATUS CHANGES ###################
def notify_queue_change(state):
    _notify_on_channel("s_queue_changed", state)


def notify_volume_change(state):
    _notify_on_channel("s_volume_changed", state)


def notify_position_change(state):
    _notify_on_channel("s_position_changed", state)


def _notify_on_channel(channel, msg_dict):
    ConcertEventsSockets.emit(channel, json.dumps(msg_dict), include_self=True)


