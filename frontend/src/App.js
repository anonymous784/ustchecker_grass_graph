import React, { Component } from 'react';
import './App.css';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import ReactLoading from 'react-loading';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      checkerId: '',
      base64Image: '',
      loading: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.handlePost = this.handlePost.bind(this);
  }

  componentDidMount(){
    document.title = "ustchecker grass graph"
  }

  handleChange(event) {
    this.setState({checkerId: event.target.value});
  }

  handlePost(event) {
    const id = this.state.checkerId;
    this.setState({
      checkerId: '',
      base64Image: '',
      loading: true
    })

    const body = JSON.stringify({
      id: id
    });
    fetch(
      'https://asia-northeast1-develop-187803.cloudfunctions.net/ustchecker_grass_graph',
      {
        method: 'POST',
        body: body,
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors'
      }
    )
    .then(response => {
      if (response.status !== 200) {
        console.error('handlePost');
        console.log(response);
      }
      return response.json();
    })
    .then(data => {
      this.setState({
        base64Image: data.base64_image,
        loading: false
      });
    });
  }


  render() {
    const Loading = () => {
      return(
        <ReactLoading className="preloader" type="spin" color="#3F53AF" height={'10%'} width={'10%'} />
      )
    };

    return (
      <div className="App">
        <AppBar position="static">
          <Toolbar>
            <Typography variant="title" color="inherit">
              ustchecker grass graph
            </Typography>
          </Toolbar>
        </AppBar>

        <form className="form">
          <TextField
            id="checker_id"
            label="チェッカーの登録ID"
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
        </form>

        <div className="image" style={{ textAlign: 'center' }}>
          {this.state.loading && <Loading/>}
          {this.state.base64Image && <img src={`data:image/png;base64,${this.state.base64Image}`}/>}
        </div>

      </div>
    );
  }
}

export default App;

