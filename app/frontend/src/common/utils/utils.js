window.FileAPI = {
    debug: true
};

var resizedataURL = function (datas, wantedWidth, wantedHeight, callback) {
    // We create an image to receive the Data URI
    var img = document.createElement('img');

    // When the event "onload" is triggered we can resize the image.
    img.onload = function () {
        // We create a canvas and get its context.
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');

        // We set the dimensions at the wanted size.
        canvas.width = wantedWidth;
        canvas.height = wantedHeight;

        // We resize the image with the canvas method drawImage();
        ctx.drawImage(this, 0, 0, wantedWidth, wantedHeight);

        var dataURI = canvas.toDataURL();

        callback(dataURI);
        /////////////////////////////////////////
        // Use and treat your Data URI here !! //
        /////////////////////////////////////////
    };

    // We put the Data URI in the image's src attribute
    img.src = datas;
};

var range = function (start, end) {
    var arr = [];
    while (start <= end) {
        arr.push(start++);
    }
    return arr;
};

var predicatBy = function (prop) {
    return function (a, b) {
        if (a[prop] > b[prop]) {
            return 1;
        } else if (a[prop] < b[prop]) {
            return -1;
        }
        return 0;
    };
};

var addDays = function (theDate, days) {
    return new Date(theDate.getTime() + days * 24 * 60 * 60 * 1000);
};

function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
