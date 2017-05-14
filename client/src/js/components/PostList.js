var Post = require("./Post");

var PostList = React.createClass({
    render: function() {
        var commentNodes = this.props.data.map(function(comment) {
            return (
                <Post time={comment.Time} key={"Post-" + comment.ID}>
                    {comment.Message}
                </Post>
            ) 
        });
        return (
            <div className="postList">
                {commentNodes.reverse()}
            </div>
        );
    }
});

module.exports = PostList;