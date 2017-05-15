var Panel = require("react-bootstrap/lib/Panel");
var Grid = require("react-bootstrap/lib/Grid");
var Row = require("react-bootstrap/lib/Row");
var Col = require("react-bootstrap/lib/Col");
var PostList = require("./PostList");
var PostForm = require("./PostForm");

var PostBox = React.createClass({
    getInitialState: function() {
        return {data: [], UserID: null};
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
    loadPostsFromServer: function(count) {
        var query = "?UserID=" + this.state.UserID;
        if (typeof(count)!=='undefined') {
            query = query + "&count=" + count.toString();
        }
        $.ajax({
            url: this.props.pollUrl + query,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({data: this.state.data.concat(data["data"])});
                this.loadPostsFromServer();
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
        })
    },
    componentDidMount: function() {
        var self = this;
        self.checkinWithServer(function() {
            self.loadPostsFromServer(self.props.batchSize);
        });        
    },
    render: function() {
        return (
            <Grid>
                <Row>
                    <Col mdOffset={3} md={6} sm={12}>
                        <Panel header="DownTo" className="postBox">
                            <PostForm onPostSubmit={this.handlePostsSubmit} />
                            <PostList data={this.state.data}/>
                        </Panel>
                    </Col>
                </Row>
            </Grid>
        )
    }
});

module.exports = PostBox;