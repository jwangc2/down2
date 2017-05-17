var ListGroup = require("react-bootstrap/lib/ListGroup");
var ListGroupItem = require("react-bootstrap/lib/ListGroupItem");
var Emergency = require("./Emergency");

var EmergencyList = React.createClass({
    render: function() {
        var self = this;
        var eNodes = this.props.data.map(function(dataEntry) {
            return (
                <ListGroupItem
                    key={"Emergency-" + dataEntry["ID"]}
                    style={{"paddingTop": "0px", "paddingBottom": "0px"}}
                    bsStyle="danger"
                    >
                    <Emergency
                        src={dataEntry["Source"]}
                        msg={dataEntry["Message"]}
                        >
                    </Emergency>
                </ListGroupItem>
            );
        });
        return (
            <ListGroup className="emergencyList">
                {eNodes.reverse()}
            </ListGroup>
        );
    }
});

module.exports = EmergencyList;