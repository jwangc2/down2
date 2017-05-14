var Post = React.createClass({
    rawMarkup: function() {
        return this.props.children
    },
    
    render: function() {       
        return (
            <div className="post">
                <span>{this.props.time}: {this.rawMarkup()}</span>
            </div>
       )
   } 
});

module.exports = Post;