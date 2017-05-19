var Emergency = React.createClass({
    onClose: function() {
        this.props.onClose(this.props.eID);
    },
    render: function() {
        return (
            <div className="emergency">
                <a href="#" onClick={this.onClose} style={{marginRight: "10px"}}><i className="fa fa-times"></i></a>
                <span>[{this.props.src}]: {this.props.msg}</span>
            </div>
        );
    }
});

module.exports = Emergency;