var PostBox = require("./components/PostBox");

ReactDOM.render(
    <PostBox
        pollUrl="/api/posts"
        submitUrl="/api/posts/submit"
        likeUrl="/api/posts/like"
        checkinUrl="/api/checkin"
        longPollInterval={30000}
        batchSize={15}
        />,
    document.getElementById('content')
);