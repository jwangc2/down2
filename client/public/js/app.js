function getWeather() {
    return "Any"
}

function getTemperature() {
    return 80
}

function buildPost(message) {
    return {
        Message: message,
        Weather: getWeather(),
        Temperature: getTemperature()
    }
}


var PostList = React.createClass({
    render: function() {
        var commentNodes = this.props.data.map(function(comment) {
            return (
                <Post time={comment.Time} key={comment.ID}>
                    {comment.Message}
                </Post>
            ) 
        });
        return (
            <div className="postList">
                {commentNodes}
            </div>
        )
    }
});

var PostForm = React.createClass({
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
        this.props.onPostSubmit(buildPost(text))
        this.setState({text: ''});
    },
    render: function() {
        return (
            <form className="postForm" onSubmit={this.handleSubmit}>
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

var PostBox = React.createClass({
    loadPostsFromServer: function(cursor) {
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
                this.loadPostsFromServer()
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
            <div className="postBox">
                <h1>Posts</h1>
                <PostList data={this.state.data}/>
                <PostForm onPostSubmit={this.handlePostsSubmit} />
            </div>
        )
    }
});

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

ReactDOM.render(
    <PostBox pollUrl="/api/posts" submitUrl="/api/posts/submit" longPollInterval={30000} />,
    document.getElementById('content')
);