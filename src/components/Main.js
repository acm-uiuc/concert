import React, { Component } from "react";
import "./Main.scss";
import ReactModalLogin from 'react-modal-login';
import SearchBar from "./SearchBar";
import { Button } from 'react-bootstrap';

export default class Main extends Component {

  constructor(props) {
    super(props);

    this.state = {
      showModal: false,
      loggedIn: false,
      loading: false,
      error: null
    };
  }

  async componentWillMount() {
    const current_user = await fetch('http://0.0.0.0:5000/user', {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log(current_user);
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
      this.setState({error: 'ahhh'});
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
    if (!this.state.loggedIn) {
      this.openModal('login');
      return;
    }

    this.setState({loggedIn: false});
  }

  render() {
    return (
      <div id="main-root">
        <SearchBar loggedIn={this.state.loggedIn}/>

        <Button
          id="login-btn"
          onClick={this.onLoginClicked.bind(this)}>
          {this.state.loggedIn ? 'Logout' : 'Login'}
        </Button>

        <ReactModalLogin
          visible={this.state.showModal}
          onCloseModal={this.closeModal.bind(this)}
          loading={this.state.loading}
          initialTab={this.state.initialTab}
          error={this.state.error}
          startLoading={() => {this.setState({loading: true})}}
          finishLoading={() => {this.setState({loading: false})}}
          loginError={{label: "Invalid username or password. Please try again."}}
          form={{
            onLogin: this.onLogin.bind(this),
            loginBtn: {label: "Sign In"},
            loginInputs: [
              {id: 'netid', placeholder: 'NetID'},
              {type: 'password', id: 'password', placeholder: 'Password'}
            ]
          }}
        />
      </div>
    );
  }
}
