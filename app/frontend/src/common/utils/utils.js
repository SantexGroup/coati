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
