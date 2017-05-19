var ListGroup = require("react-bootstrap/lib/ListGroup");
var ListGroupItem = require("react-bootstrap/lib/ListGroupItem");
var Emergency = require("./Emergency");

var EmergencyList = React.createClass({
    render: function() {
        var self = this;
        var eNodes = Object.keys(this.props.data).map(function(eID) {
            var dataEntry = self.props.data[eID];
            return (
                <ListGroupItem
                    key={"Emergency-" + dataEntry["ID"]}
                    style={{"paddingTop": "0px", "paddingBottom": "0px"}}
                    bsStyle="danger"
                    >
                    <Emergency
                        eID={eID}
                        src={dataEntry["Source"]}
                        msg={dataEntry["Message"]}
                        onClose={self.props.onEmergencyDismissed}
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