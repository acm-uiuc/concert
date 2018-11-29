import React, { Component } from "react";
import "./App.scss";
import Main from "./components/Main";
import SideBar from "./components/SideBar";
import StatusBar from "./components/StatusBar";

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
