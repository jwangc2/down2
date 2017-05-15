var ListGroup = require("react-bootstrap/lib/ListGroup");
var ListGroupItem = require("react-bootstrap/lib/ListGroupItem");
var Well = require("react-bootstrap/lib/Well");
var Post = require("./Post");

var PostList = React.createClass({
    getInitialState: function() {
        return {liked: new Set()};
    },
    handleLike: function(id) {
        if (this.state.liked.has(id)) {
            this.state.liked.delete(id);
        } else {
            this.state.liked.add(id);
        }
        this.setState({liked: this.state.liked});
    },
    render: function() {
        var self = this;
        var commentNodes = this.props.data.map(function(postEntry) {
            return (
                <ListGroupItem key={"Post-" + postEntry.ID}>
                    <Post
                        time={postEntry.Time}
                        postID={postEntry.ID}
                        likes={postEntry.Likes}
                        liked={self.state.liked.has(postEntry.ID)}
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