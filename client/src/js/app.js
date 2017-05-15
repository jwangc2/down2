var PostBox = require("./components/PostBox");

ReactDOM.render(
    <PostBox
        pollUrl="/api/posts"
        submitUrl="/api/posts/submit"
        checkinUrl="/api/checkin"
        longPollInterval={30000}
        batchSize={15}
        />,
    document.getElementById('content')
);