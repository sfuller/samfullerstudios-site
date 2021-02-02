SFSUtil = {};

SFSUtil.promiseHttp = function(method, url) {
    const request = new XMLHttpRequest();
    const promise = new Promise((resolve, reject) => {
        request.open(method, url, true);
        request.onload = function() {
            resolve(this);
        };
        request.onerror = function() {
            reject(this);
        }
        request.send();
    });
    return {
        promise: promise,
        request: request
    };
}
