var Emergency = React.createClass({
    getInitialState: function() {
        return ({closed: false});
    },
    onClose: function() {
        this.setState({closed: true});
    },
    render: function() {
        if (this.state.closed) {
            return null;
        }
        return (
            <div className="emergency">
                <a href="#" onClick={this.onClose} style={{marginRight: "10px"}}><i className="fa fa-times"></i></a>
                <span>[{this.props.src}]: {this.props.msg}</span>
            </div>
        );
    }
});

module.exports = Emergency;