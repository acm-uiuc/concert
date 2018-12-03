import React, { Component } from "react";
import "./App.css";

class App extends Component {
  render() {
    return (
      <div>

        <div class="sidenav">
        	<div class = "sidecontainer">
          	<a href="#about">Link 1</a>
          	<a href="#services">Link 2</a>
          	<a href="#clients">Link 3</a>
          	<a href="#contact">Link 4</a>
         	 </div>
        </div>
        <div className="StatusBar">
          <h1>"This is text."</h1>
        </div>
      </div>
    );
  }
}

export default App;
