import React, { Component } from "react";
import "./Main.scss";
import SearchBar from "./SearchBar";

export default class Main extends Component {
  render() {
    return (
      <div id="main-root">
        <SearchBar />
      </div>
    );
  }
}
