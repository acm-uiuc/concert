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
        <link
          rel="stylesheet"
          href="https://use.fontawesome.com/releases/v5.5.0/css/all.css"
          integrity="sha384-B4dIYHKNBt8Bc12p+WXckhzcICo0wtJAoU8YZTY5qE0Id1GSseTk6S+L3BlXeVIU"
          crossOrigin="anonymous"
        />
        <div id="content">
          <div id="controls">
            <div className="column">
              <i className="fa fa-random" aria-hidden="true" />
            </div>
            <div className="column">
              <i className="fa fa-backward" aria-hidden="true" />
            </div>
            <div className="column">
              <i className="fa fa-play play-btn fa-fw" aria-hidden="true" />
            </div>
            <div className="column">
              <i className="fa fa-forward" aria-hidden="true" />
            </div>
            <div className="column">
              <i className="fa fa-sync-alt" aria-hidden="true" />
            </div>
          </div>
          <input type="range" value="30" />
        </div>
      </div>
    );
  }
}
