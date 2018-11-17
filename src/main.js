import React, { Component } from "react";
import "./Main.scss";
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider'
import SearchBar from 'material-ui-search-bar';

export default class Main extends Component {
  render() {
    return (
      <div id="main-root">
        <MuiThemeProvider>
          <SearchBar
            onChange={() => console.log('onChange')}
            onRequestSearch={() => console.log('onRequestSearch')}
            style={{
              margin: 'auto',
              maxWidth: 800,
              flexGrow: 1
            }}
          />
        </MuiThemeProvider>
      </div>
    );
  }
}
