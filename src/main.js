import React, { Component } from "react";
import "./Main.css";

export default class Main extends Component {
  render() {
    return (
      <div id="main-root">
        <h1>Hello, {this.props.name}</h1>
      </div>
    );
  }
}
