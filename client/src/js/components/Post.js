var Post = React.createClass({
    rawMarkup: function() {
        return this.props.children
    },
    handleLike: function(e) {
        e.preventDefault();
        this.props.onLike(this.props.postID);
    },    
    render: function() {       
        return (
            <div className="post">
                <a href="#" onClick={this.handleLike} style={{marginRight: "10px"}}><i className={this.props.liked ? "fa fa-heart": "fa fa-heart-o"}></i></a>
                <span>{this.props.likes.toString() + "..."} {this.props.time}: {this.rawMarkup()}</span>
            </div>
        );
   } 
});

module.exports = Post;