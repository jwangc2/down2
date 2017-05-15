var Location = require("../model/Location");
var Button = require("react-bootstrap/lib/Button");
var FormGroup = require("react-bootstrap/lib/FormGroup");
var ControlLabel = require("react-bootstrap/lib/ControlLabel");
var FormControl = require("react-bootstrap/lib/FormControl");

function getLocation(onSuccess) {
    $.get("http://ipinfo.io/json", function (response) {
        var locs = response.loc.split(",")
        var lat = parseFloat(locs[0].trim())
        var lon = parseFloat(locs[1].trim())
        onSuccess(new Location(lat, lon));
    });
    return null;
}


function getWeatherData(loc, onSuccess) {
    if (loc != null) {
        $.get("/api/weather?lat=" + loc.latitude.toString() + "&lon=" + loc.longitude.toString(), function(response) {
            onSuccess(response);
        });
    }
}

function buildPost(message, weatherData) {    
    return {
        Message: message,
        Weather: weatherData['Weather'],
        Temperature: weatherData['Temperature']
    }
}

var PostForm = React.createClass({
    getInitialState: function() {
        return ({text: '', location: null});
    },
    componentDidMount: function() {
        var self = this;
        var onSuccess = function(loc) {
            self.setState({location: loc});
        };
        getLocation(onSuccess);
    },
    handleAuthorChange: function(e) {
        this.setState({author: e.target.value});
    },
    handleTextChange: function(e) {
        this.setState({text: e.target.value});
    },
    handleSubmit: function(e) {
        e.preventDefault();
        var text = this.state.text.trim();
        if (!text) {
            return;
        }
        self = this;
        getWeatherData(this.state.location, function(weatherData) {
            var post = buildPost(text, weatherData);
            if (post != null) {
                self.props.onPostSubmit(post)
                self.setState({text: ''});
            }
        });
    },
    render: function() {
        return (
            <form className="postForm" onSubmit={this.handleSubmit}>
                <FormGroup>
                    <ControlLabel>I'm Down</ControlLabel>
                    <FormControl
                        componentClass="input"
                        type="text"
                        placeholder="to..."
                        value={this.state.text}
                        onChange={this.handleTextChange}
                    />
                    <Button type="submit" bsSize="xsmall" block>
                        Submit
                    </Button>
                </FormGroup>
            </form>
        )
    }
});

module.exports = PostForm;