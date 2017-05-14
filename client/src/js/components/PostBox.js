var Panel = require("react-bootstrap/lib/Panel");
var PostList = require("./PostList");
var PostForm = require("./PostForm");

var PostBox = React.createClass({
    loadPostsFromServer: function(cursor) {
        var query = "";
        if (typeof(cursor)!=='undefined') {
            query = "?cursor=" + cursor.toString();
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
        this.loadPostsFromServer(-1);
    },
    render: function() {
        return (
            <Panel header="DownTo" className="postBox">
                <PostForm onPostSubmit={this.handlePostsSubmit} />
                <PostList data={this.state.data}/>
            </Panel>
        )
    }
});

module.exports = PostBox;