import React, { Component } from "react";
import IconButton from "@material-ui/core/IconButton";
import Search from "@material-ui/icons/Search";
import PlayCircleOutline from "@material-ui/icons/PlayCircleOutline";
import QueueMusic from "@material-ui/icons/QueueMusic";
import FastForward from "@material-ui/icons/FastForward";
import FastRewind from "@material-ui/icons/FastRewind";
import Shuffle from "@material-ui/icons/Shuffle";
import "./StatusBar.scss";

export default class StatusBar extends Component {
  render() {
    return (
        <div className="StatusBar">
          <IconButton class = "button rewind" onClick={() => {}}>
              <FastRewind />
          </IconButton>
          <IconButton class = "button play-pause" onClick={() => {}}>
              <PlayCircleOutline />
          </IconButton>
          <IconButton class = "button forward" onClick={() => {}}>
              <FastForward />
          </IconButton>
          <IconButton class = "button shuffle" onClick={() => {}}>
              <Shuffle />
          </IconButton>
          <IconButton class = "button queue" onClick={() => {}}>
              <QueueMusic />
          </IconButton>
        </div>
    );
  }
}