import React, { Component } from "react";

export const MediaControllerText = () => {
  return (
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
  );
};

export default MediaControllerText;
