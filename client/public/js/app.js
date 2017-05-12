function getWeather() {
    return "Any"
}

function getTemperature() {
    return 80
}

function buildComment(message) {
    return {
        Message: message,
        Weather: getWeather(),
        Temperature: getTemperature()
    }
}


var CommentList = React.createClass({
    render: function() {
        var commentNodes = this.props.data.map(function(comment) {
            return (
                <Comment time={comment.Time} key={comment.ID}>
                    {comment.Message}
                </Comment>
            ) 
        });
        return (
            <div className="commentList">
                {commentNodes}
            </div>
        )
    }
});

var CommentForm = React.createClass({
    getInitialState: function() {
        return ({text: ''});
    },
    handleAuthorChange: function(e) {
        this.setState({author: e.target.value});
    },
    handleTextChange: function(e) {
        this.setState({text: e.target.value});
    },
    handleSubmit: function(e) {
        e.preventDefault();
        var text = this.state.text.trim();
        if (!text) {
            return;
        }
        this.props.onCommentSubmit(buildComment(text))
        this.setState({text: ''});
    },
    render: function() {
        return (
            <form className="commentForm" onSubmit={this.handleSubmit}>
                <input
                    type="text"
                    placeholder="Say something..."
                    value={this.state.text}
                    onChange={this.handleTextChange}
                />
                <input type="submit" value="Post" />
            </form>
        )
    }
});

var CommentBox = React.createClass({
    loadCommentsFromServer: function(cursor) {
        var query = ""
        if (typeof(cursor)!=='undefined') {
            query = "?cursor=" + cursor.toString()
        }
        $.ajax({
            url: this.props.pollUrl + query,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({data: this.state.data.concat(data["data"])});
                this.loadCommentsFromServer()
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                // todo: prompt user to refresh?
            }.bind(this)
        });
    },
    handleCommentsSubmit: function(comment) {
        $.ajax({
            url: this.props.submitUrl,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify(comment),
            success: function(data) {
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
        this.loadCommentsFromServer(-1);
    },
    render: function() {
        return (
            <div className="commentBox">
                <h1>Comments</h1>
                <CommentList data={this.state.data}/>
                <CommentForm onCommentSubmit={this.handleCommentsSubmit} />
            </div>
        )
    }
});

var Comment = React.createClass({
    rawMarkup: function() {
        return this.props.children
    },
    
    render: function() {       
       return (
        <div className="comment">
            <span>{this.props.time}: {this.rawMarkup()}</span>
        </div>
       )
   } 
});

ReactDOM.render(
    <CommentBox pollUrl="/api/posts" submitUrl="/api/posts/submit" longPollInterval={30000} />,
    document.getElementById('content')
);