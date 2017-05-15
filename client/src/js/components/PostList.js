var ListGroup = require("react-bootstrap/lib/ListGroup");
var ListGroupItem = require("react-bootstrap/lib/ListGroupItem");
var Well = require("react-bootstrap/lib/Well");
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
        var commentNodes = this.props.data.map(function(postEntry) {
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
            <Well className="postList">
                <ListGroup>
                    {commentNodes.reverse()}
                </ListGroup>
            </Well>
        );
    }
});

module.exports = PostList;