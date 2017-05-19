var Panel = require("react-bootstrap/lib/Panel");
var Grid = require("react-bootstrap/lib/Grid");
var Row = require("react-bootstrap/lib/Row");
var Col = require("react-bootstrap/lib/Col");
var Well = require("react-bootstrap/lib/Well");
var PostList = require("./PostList");
var PostForm = require("./PostForm");
var EmergencyList = require("./EmergencyList");

var PostBox = React.createClass({
    getInitialState: function() {
        return {posts: [], emergencies: [], UserID: null};
    },
    checkinWithServer: function(successHandler) {
        $.ajax({
            url: this.props.checkinUrl,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({UserID: data["UserID"]});
                successHandler();
            }.bind(this),
            error: function(xhr, status, err) {
                console.log(this.props.checkinUrl, status, err.toString());
            }.bind(this)
        });
    },
    updateData: function(oldData, newData, matchFn) {
        var match, i, j;
        for (i = 0; i < newData.length; i++) {
            match = -1;
            j = 0;
            while(j < oldData.length && match == -1) {
                if (matchFn(oldData[j], newData[i])) {
                    match = j;
                }
                j += 1;
            }
            if (match == -1) {
                // append
                oldData.push(newData[i]);
            } else {
                // update
                oldData[match] = newData[i];
            }
        }
    },
    loadPostsFromServer: function(count) {
        var query = "?UserID=" + this.state.UserID;
        if (typeof(count)!=='undefined') {
            query = query + "&count=" + count.toString();
        }
        $.ajax({
            url: this.props.pollPostsUrl + query,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.updateData(this.state.posts, data["data"], function(oldDatum, newDatum) {
                    return (oldDatum["ID"] == newDatum["ID"]);
                });
                this.setState({posts: this.state.posts});
                this.loadPostsFromServer();
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                // todo: prompt user to refresh?
            }.bind(this)
        });
    },
    loadEmergenciesFromServer: function(count) {
        var query = "?UserID=" + this.state.UserID;
        if (typeof(count)!=='undefined') {
            query = query + "&count=" + count.toString();
        }
        $.ajax({
            url: this.props.pollEmergenciesUrl + query,
            dataType: 'json',
            cache: false,
            success: function(data) {
                var emergencyData = data["emergencies"];
                var eDict = {};
                var e;
                for (var i = 0; i < emergencyData.length; i++) {
                    e = emergencyData[i];
                    eDict[e["ID"]] = e;
                }
                this.setState({emergencies: eDict});
                this.loadEmergenciesFromServer();
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                // todo: prompt user to refresh?
            }.bind(this)
        });
    },
    handlePostsSubmit: function(post) {
        var mData = post
        mData["UserID"] = this.state.UserID;
        $.ajax({
            url: this.props.submitUrl,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify(mData),
            success: function(data) {
                // do nothing
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    handlePostLiked: function(postID, onSuccess) {
        var mData = {
            "PostID": postID,
            "UserID": this.state.UserID
        };
        $.ajax({
            url: this.props.likeUrl,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify(mData),
            success: function(data) {
                onSuccess(data);
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    handleEmergencyDismissed: function(eID) {
        var self = this;
        var filtered = Object.keys(this.state.emergencies).reduce(function(filtered, key) {
            if (self.state.emergencies[key]["ID"] != eID) {
                filtered[key] = self.state.emergencies[key];
            }
            return filtered;
        }, {});
        
        this.setState({emergencies: filtered});
    },
    componentDidMount: function() {
        var self = this;
        self.checkinWithServer(function() {
            self.loadPostsFromServer(self.props.batchSize);
            self.loadEmergenciesFromServer(-1);
        });        
    },
    render: function() {
        return (
            <Grid>
                <Row>
                    <Col mdOffset={3} md={6} sm={12}>
                        <Panel header="DownTo" className="postBox">
                            <PostForm onPostSubmit={this.handlePostsSubmit} />
                            <Well>
                                <EmergencyList onEmergencyDismissed={this.handleEmergencyDismissed} data={this.state.emergencies}></EmergencyList>
                                <PostList onPostLiked={this.handlePostLiked} data={this.state.posts}/>
                            </Well>
                        </Panel>
                    </Col>
                </Row>
            </Grid>
        )
    }
});

module.exports = PostBox;