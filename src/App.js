import React, { Component } from "react";
import "./App.css";

class App extends Component {
  render() {
    return (
      <div id="wrapper">
        <div id="container">
          <ul class="songs blur">
            <li>
              <img src="http://enwaara.se/codepen/post-malone.jpg" />
              <h2>Post Malone</h2>
              <p>
                <i class="fas fa-compact-disc" />I Fall Apart
              </p>
            </li>
          </ul>

          <div class="time blur">
            <p>0:00</p>
            <p>3:43</p>
            <div id="time" />
          </div>

          <div class="controls blur">
            <i class="fas fa-step-backward arrow" />
            <i class="far fa-play-circle play-button" />
            <i class="fas fa-step-forward arrow" />
          </div>

          <div class="options blur">
            <i class="fas fa-random option" />
            <i class="fas fa-sync-alt option" />
            <i class="fas fa-ellipsis-h menu-icon" />
          </div>

          <div class="menu">
            <i class="fas fa-times close-icon" />

            <ul class="menu-items">
              <li class="favorite">
                <i class="far fa-heart" />
                Fav
              </li>
              <li>
                <i class="fas fa-music">
                  <i class="fas fa-plus-circle" />
                </i>
                Fav
              </li>
              <li>
                <i class="fas fa-compact-disc" />
                Album
              </li>
              <li>
                <i class="fas fa-user" />
                Artist
              </li>
              <li>
                <i class="fas fa-share-square" />
                Something
              </li>
            </ul>

            <div class="sound">
              <i class="fas fa-volume-down" />
              <div id="volume" />
              <i class="fas fa-volume-up" />
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
