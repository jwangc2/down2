var Button = require("react-bootstrap/lib/Button");
var FormGroup = require("react-bootstrap/lib/FormGroup");
var ControlLabel = require("react-bootstrap/lib/ControlLabel");
var FormControl = require("react-bootstrap/lib/FormControl");

function buildPost(message) {    
    return {
        Message: message
    }
}

var PostForm = React.createClass({
    getInitialState: function() {
        return ({text: ''});
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
        var post = buildPost(text);
        if (post != null) {
            this.props.onPostSubmit(post)
            this.setState({text: ''});
        }
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