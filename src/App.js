import React, { Component } from "react";
import "./App.scss";
import Main from "./Main";
import SideBar from "./SideBar";
import StatusBar from "./StatusBar";

class App extends Component {
  render() {
    return (
      <div>
        <SideBar />
        <Main />
        <StatusBar />
      </div>
    );
  }
}

export default App;
