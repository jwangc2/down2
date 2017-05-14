var PostBox = require("./components/PostBox");

ReactDOM.render(
    <PostBox pollUrl="/api/posts" submitUrl="/api/posts/submit" longPollInterval={30000} />,
    document.getElementById('content')
);