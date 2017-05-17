var PostBox = require("./components/PostBox");

ReactDOM.render(
    <PostBox
        pollPostsUrl="/api/posts"
        pollEmergenciesUrl="/api/emergency"
        submitUrl="/api/posts/submit"
        likeUrl="/api/posts/like"
        checkinUrl="/api/checkin"
        longPollInterval={30000}
        batchSize={15}
        />,
    document.getElementById('content')
);