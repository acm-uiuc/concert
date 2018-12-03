import React, { Component } from "react";
import "./App.scss";
import Main from "./components/Main";
import SideBar from "./components/SideBar";
import StatusBar from "./components/StatusBar";

class App extends Component {
  constructor() {
    super();

    this.state = {
      artwork: null
    }

    window.appComponent = this;
  }

  updateClient = (serverState) => {
    if (serverState == null) {
      return;
    }

    if (this.state.artwork !== serverState.player.current_track_info.thumbnail_url) {
      this.setState({artwork: serverState.player.current_track_info.thumbnail_url});
    }
  }

  render() {
    return (
      <div id="main-container">
          <SideBar />
          <Main artwork={this.state.artwork}/>
          <StatusBar />
      </div>
    );
  }
}

export default App;
