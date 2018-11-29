import React, { Component } from "react";
import "./Main.scss";
import SearchBar from "./SearchBar";
import io from '../helpers/io'

export default class Main extends Component {

  handleClick() {
    console.log('hello!');
    io.emit('clicked');
  }

  render() {
    return (
      <div id="main-root">
        <SearchBar />
        <button onClick={this.handleClick}>
          Click me!
        </button>
      </div>
    );
  }
}
