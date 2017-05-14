var Panel = require("react-bootstrap/lib/Panel");
var Grid = require("react-bootstrap/lib/Grid");
var Row = require("react-bootstrap/lib/Row");
var Col = require("react-bootstrap/lib/Col");
var PostList = require("./PostList");
var PostForm = require("./PostForm");

var PostBox = React.createClass({
    loadPostsFromServer: function(count) {
        var query = "";
        if (typeof(count)!=='undefined') {
            query = "?count=" + count.toString();
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
    handlePostsSubmit: function(comment) {
        $.ajax({
            url: this.props.submitUrl,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify(comment),
            success: function(data) {
                // do nothing
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        })
    },
    getInitialState: function() {
        return {data: []};
    },
    componentDidMount: function() {
        this.loadPostsFromServer(this.props.batchSize);
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