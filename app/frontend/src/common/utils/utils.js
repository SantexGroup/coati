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

var addDays = function(theDate, days) {
    return new Date(theDate.getTime() + days*24*60*60*1000);
};

function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
