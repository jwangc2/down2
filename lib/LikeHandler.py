from lib.JsonHandler import JsonHandler
import tornado.web
from tornado.concurrent import Future
from tornado import gen

class LikeHandler(JsonHandler):
    def initialize(self, postBuffer, emergencyBuffer, httpClient, userActivity, weatherCategories):
        self.postBuffer = postBuffer
        self.userActivity = userActivity        

    @gen.coroutine
    def post(self):
        userID = self.request.arguments.get("UserID", None)
        if userID is None or userID not in self.userActivity.keys():
            self.write_error_custom(401, message="Unauthorized request")
        else:
            postID = self.request.arguments.get("PostID", None)
            if postID is None:
                self.write_error_custom(400, message="Bad Post ID")
            else:
                # Toggle like status
                liked = postID in self.userActivity[userID]["Liked"]
                if liked:
                    self.userActivity[userID]["Liked"].remove(postID)
                    self.postBuffer.removeLike(postID)
                else:
                    self.userActivity[userID]["Liked"].add(postID)
                    self.postBuffer.addLike(postID)

                # Yield for async triage purposes
                likeFuture = Future()
                likeFuture.set_result(not liked)
                result = yield likeFuture
                
                # Return the de facto result
                self.response = {"Liked": result}
                self.write_json()