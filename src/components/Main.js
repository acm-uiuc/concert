import React, { Component } from "react";
import "./Main.scss";
import ReactModalLogin from 'react-modal-login';
import SearchBar from "./SearchBar";
import { Button } from 'react-bootstrap';
import {isURL} from '../helpers/helpers';
import io from '../helpers/io';

export default class Main extends Component {

  constructor(props) {
    super(props);    

    this.state = {
      showModal: false,
      loggedIn: false,
      loading: false,
      error: null,
      searchValue: null
    };

    this.searchForm = React.createRef();
  }

  componentDidMount() {
    this.searchForm.current.addEventListener('submit', this.handleSearchSubmit);
  }

  async onLogin() {
    const netid = document.querySelector('#netid').value;
    const password = document.querySelector('#password').value;

    const loginAttempt = await fetch('http://0.0.0.0:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({username: netid, password})
    });

    if (loginAttempt.status !== 200) {
      this.setState({error: true});
      return;
    }

    this.closeModal();
    this.setState({loggedIn: true, loading: false});
  }

  openModal() {
    this.setState({
      initialTab: 'login'
    }, () => {
      this.setState({
        showModal: true,
      });
    });
  }

  closeModal() {
    this.setState({showModal: false, error: null});
  }

  onLoginClicked() {
    this.openModal('login');
  }

  async onLogoutClicked() {
    this.setState({loggedIn: false});

    const logoutAttempt = await fetch('http://0.0.0.0:5000/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log(logoutAttempt);
  }

  handleSearchSubmit = (event) => {
    event.preventDefault();

    if (!isURL(this.state.searchValue) ||
        (!this.state.searchValue.includes("youtube.com") &&
         !this.state.searchValue.includes("soundcloud.com"))) {
      alert("Please enter a valid url");
    } else {
        io.emit('c_queue_song', this.state.searchValue);
    }
  }

  handleNewSearchValue = (newValue) => {
    this.setState({searchValue: newValue});
  }

  render() {
    return (
      <div id="main-root" style={{backgroundImage: `url(${this.props.artwork})`}}>
        <form id="search-form" ref={this.searchForm}>
          <SearchBar loggedIn={this.state.loggedIn} onChange={this.handleNewSearchValue}/>
        </form>

        <Button
          id="login-btn"
          onClick={this.state.loggedIn ? this.onLogoutClicked.bind(this) : this.onLoginClicked.bind(this)}>
          {this.state.loggedIn ? 'Logout' : 'Login'}
        </Button>

        <ReactModalLogin
          visible={this.state.showModal}
          onCloseModal={this.closeModal.bind(this)}
          loading={this.state.loading}
          initialTab={this.state.initialTab}
          error={this.state.error}
          startLoading={() => this.setState({loading: true})}
          finishLoading={() => this.setState({loading: false})}
          loginError={{label: "Invalid username or password. Please try again."}}
          form={{
            onLogin: this.onLogin.bind(this),
            loginBtn: {label: "Sign In"},
            loginInputs: [
              {name: 'username', id: 'netid', placeholder: 'NetID'},
              {type: 'password', id: 'password', placeholder: 'Password'}
            ]
          }}
        />
      </div>
    );
  }
}