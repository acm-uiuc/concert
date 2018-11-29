import React, { Component } from "react";
import "./SideBar.scss";

export default class SideBar extends Component {
  render() {
    return (
        <div className="sidenav">
            <a href="#about">Link 1</a>
            <a href="#services">Link 2</a>
            <a href="#clients">Link 3</a>
            <a href="#contact">Link 4</a>
        </div>
    );
  }
}