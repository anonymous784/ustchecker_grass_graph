import React, { Component } from 'react';
import './App.css';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      checkerId: '',
      base64Image: ''
    };

    this.handleChange = this.handleChange.bind(this);
    this.handlePost = this.handlePost.bind(this);
  }

  handleChange(event) {
    this.setState({checkerId: event.target.value});
  }

  handlePost(event) {
    const id = this.state.checkerId;
    fetch(`https://asia-northeast1-develop-187803.cloudfunctions.net/ustchecker_grass_graph?id=${id}&format=base64`)
    .then(response => {
      if (response.status !== 200) {
        console.error('handleCheckUrl');
      }
      return response.json();
    })
    .then(data => {
      this.setState({
        base64Image: data.base64_image
      });
    });
  }


  render() {
    return (
      <div className="App">
        <AppBar position="static">
          <Toolbar>
            <Typography variant="title" color="inherit">
              Photos
            </Typography>
          </Toolbar>
        </AppBar>
        <TextField
          id="checker_id"
          label="チェッカーの登録ID"
          placeholder="89"
          margin="normal"
          style={{ margin: '30px' }}
          onChange={this.handleChange}
        />
        <Button
          variant="contained"
          color="primary"
          disabled={!this.state.checkerId}
          onClick={this.handlePost}
        >
          画像生成
        </Button>
      </div>
    );
  }
}

export default App;

