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

var sortHtmlElements = function (elements, source, childType, attrCheck) {
    var listItems = elements.children(childType).get();
    listItems.sort(function (a, b) {
        var compA, compB;
        compA = source.filter(function (item) {
            return item.id === parseInt($(a).attr(attrCheck), 10);
        });
        compB = source.filter(function (item) {
            return item.id === parseInt($(b).attr(attrCheck), 10);
        });
        if (compA[0].order < compB[0].order) {
            return -1;
        } else if (compA[0].order > compB[0].order) {
            return 1;
        }
        return 0;
    });
    return listItems;
};

var sortcards = function (element, BoardService) {
    $(element).sortable({
        connectWith: '.connected-cards',
        placeholder: "cards_placeholder",
        revert: true,
        dropOnEmpty: true,
        items: '>li',
        tolerance: 'pointer',
        cursor: 'move',
        opacity: 0.7,
        forcePlaceholderSize: true,
        start: function (e, ui) {
            ui.placeholder.height(ui.helper.outerHeight());
        },
        receive: function (e, ui) {
            var col_id = $(element).parent().parent().attr('id');
            console.log(col_id);
            var card_id = $(ui.item).attr('id');
            BoardService.update_card_position(card_id, col_id).then(function () {
                console.log('card updated');
            }, function (err) {
                console.log(err);
            });
        }
    });
};
