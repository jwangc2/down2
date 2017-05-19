var ListGroup = require("react-bootstrap/lib/ListGroup");
var ListGroupItem = require("react-bootstrap/lib/ListGroupItem");
var Post = require("./Post");

var PostList = React.createClass({
    getInitialState: function() {
        return {liked: new Set()};
    },
    setLikeState: function(id, liked) {
        if (liked) {
            this.state.liked.add(id);
        } else {
            this.state.liked.delete(id);
        }
        this.setState({liked: this.state.liked});
    },
    handleLike: function(id) {
        this.setLikeState(id, !this.state.liked.has(id));
        var self = this;
        this.props.onPostLiked(id, function(data) {
            self.setLikeState(id, data["Liked"]);
        });
    },
    render: function() {
        var self = this;
        var postNodes = this.props.data.map(function(postEntry) {
            return (
                <ListGroupItem key={"Post-" + postEntry["ID"]}>
                    <Post
                        time={postEntry["Time"]}
                        postID={postEntry["ID"]}
                        likes={postEntry["Likes"]}
                        liked={self.state.liked.has(postEntry["ID"])}
                        onLike={self.handleLike}
                        >
                        {postEntry.Message}
                    </Post>
                </ListGroupItem>
            );
        });
        return (
            <ListGroup className="postList">
                {postNodes.reverse()}
            </ListGroup>
        );
    }
});

module.exports = PostList;