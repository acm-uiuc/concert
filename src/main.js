import React, { Component } from "react";

export default class Main extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}</h1>;
  }
}
