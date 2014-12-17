(function (angular) {

    var ImageFunction = function (q) {
        'use strict';
        var URL, createImage, getResizeArea, resizeImage;
        URL = window.URL || window.webkitURL;
        getResizeArea = function () {
            var resizeArea, resizeAreaId;
            resizeAreaId = 'fileupload-resize-area';
            resizeArea = document.getElementById(resizeAreaId);
            if (!resizeArea) {
                resizeArea = document.createElement('canvas');
                resizeArea.id = resizeAreaId;
                resizeArea.style.visibility = 'hidden';
                document.body.appendChild(resizeArea);
            }
            return resizeArea;
        };
        resizeImage = function (origImage, options) {
            var canvas, ctx, height, maxHeight, maxWidth, quality, type, width;
            maxHeight = options.resizeMaxHeight || 300;
            maxWidth = options.resizeMaxWidth || 250;
            quality = options.resizeQuality || 0.7;
            type = options.resizeType || 'image/jpg';
            canvas = getResizeArea();
            height = origImage.height;
            width = origImage.width;
            if (width > height) {
                if (width > maxWidth) {
                    height = Math.round(height *= maxWidth / width);
                    width = maxWidth;
                }
            } else {
                if (height > maxHeight) {
                    width = Math.round(width *= maxHeight / height);
                    height = maxHeight;
                }
            }
            canvas.width = width;
            canvas.height = height;
            ctx = canvas.getContext("2d");
            ctx.drawImage(origImage, 0, 0, width, height);
            return canvas.toDataURL(type, parseFloat(quality));
        };
        createImage = function (url, callback) {
            var image = new Image();
            image.onload = function () {
                callback(image);
            };
            image.src = url;
        };
        return {
            restrict: 'A',
            scope: {
                image: '=',
                resizeMaxHeight: '@?',
                resizeMaxWidth: '@?',
                resizeQuality: '@?',
                resizeType: '@?'
            },
            link: function (scope, element, attrs, ctrl) {
                var applyScope, doResizing, fileToDataURL;
                doResizing = function (imageResult, callback) {
                    createImage(imageResult.url, function (image) {
                        var dataURL = resizeImage(image, scope);
                        imageResult.resized = {
                            dataURL: dataURL,
                            type: dataURL.match(/:(.+\/.+)/)[1]
                        };
                        callback(imageResult);
                    });
                };
                applyScope = function (imageResult) {
                    scope.$apply(function () {
                        if (attrs.multiple) {
                            scope.image.push(imageResult);
                        } else {
                            scope.image = imageResult;
                        }
                    });
                };
                fileToDataURL = function (file, scope) {
                    var deferred, reader;
                    deferred = q.defer();
                    reader = new FileReader();
                    reader.onload = function (e) {
                        var imageResult;
                        imageResult = {
                            file: file,
                            url: URL.createObjectURL(file),
                            dataURL: e.target.result
                        };
                        if (scope.resizeMaxHeight || scope.resizeMaxWidth) {
                            doResizing(imageResult, function (imageResult) {
                                applyScope(imageResult);
                            });
                        } else {
                            applyScope(imageResult);
                        }
                    };
                    reader.readAsDataURL(file);
                    return deferred.promise;
                };
                element.bind('change', function (evt) {
                    if (attrs.multiple) {
                        scope.image = [];
                    }
                    var files = evt.target.files;
                    for (var i = 0; i < files.length; i++) {
                        fileToDataURL(files[i], scope);
                    }
                });
            }
        };
    };

    var Chart = function () {
        return {
            restrict: 'E',
            template: '<div></div>',
            scope: {
                chartData: "=value"
            },
            transclude: true,
            replace: true,
            link: function (scope, element, attrs) {
                var chartsDefaults = {
                    chart: {
                        renderTo: element[0],
                        type: attrs.type || null,
                        height: attrs.height || null,
                        width: attrs.width || null
                    }
                };
                scope.$watch(function () {
                    return scope.chartData;
                }, function (value) {
                    var newSettings;
                    if (!value) {
                        $(element).empty();
                        return;
                    }
                    newSettings = {};
                    angular.extend(newSettings, chartsDefaults, scope.chartData);
                    return new Highcharts.Chart(newSettings);
                });
            }
        };
    };

    var OnEscape = function () {
        return function (scope, elm, attr) {
            elm.bind('keydown', function (e) {
                if (e.keyCode === 27) {
                    scope.$apply(attr.onEsc);
                }
            });
        };
    };

    var OnEnter = function () {
        return function (scope, elm, attr) {
            elm.bind('keypress', function (e) {
                if (e.keyCode === 13) {
                    scope.$apply(attr.onEnter);
                }
            });
        };
    };

    var InlineEdit = function (timeout) {
        return {
            scope: {
                model: '=inlineEdit',
                handleSave: '&onSave',
                handleCancel: '&onCancel'
            },
            link: function (scope, elm, attr) {
                var previousValue;
                scope.editMode = false;
                scope.edit = function () {
                    scope.editMode = true;
                    previousValue = scope.model;
                    timeout(function () {
                        elm.find('input')[0].focus();
                    }, 0, false);
                };
                scope.save = function () {
                    scope.editMode = false;
                    scope.handleSave({value: scope.model});
                };
                scope.cancel = function () {
                    scope.editMode = false;
                    scope.model = previousValue;
                    scope.handleCancel({value: scope.model});
                };
            },
            template: '<input style="width: auto; display:inline-block;" class="form-control" type="text" on-enter="save()" on-esc="cancel()" ng-model="model" ng-show="editMode"><span ng-hide="editMode" ng-click="edit()"><[ model ]></span>'
        };
    };

    var TicketDetailView = function (conf) {
        return {
            restrict: 'E',
            scope: {
                reduceItem: '@reducedItem',
                sizeReducedItem: '@sizeReducedItem'
            },
            transclude: true,
            replace: true,
            templateUrl: 'ticket/ticket_quick_detail_view.tpl.html',
            link: function (scope, elem, attrs, ctrl) {
                scope.$watch('$parent.vm.loaded', function (new_val, old_val) {
                    scope.loaded = new_val;
                });

                scope.$watch('$parent.vm.ticket_detail', function (new_val, old_val) {
                    scope.model = new_val;
                    if (scope.model) {
                        angular.forEach(conf.TICKET_TYPES, function (val, key) {
                            if (val.value === scope.model.type) {
                                scope.model.type_name = val.name;
                                return;
                            }
                        });
                    }
                });
                scope.$watch('$parent.vm.ticket_clicked', function (new_val) {
                    if (new_val) {
                        $(elem).show("fold", 500);
                        $(scope.reduceItem).addClass('col-md-' + scope.sizeReducedItem, 500);
                        $(window.opera ? 'html' : 'html, body').animate({
                            scrollTop: 0
                        }, 'slow');
                    }
                });
                scope.close = function () {
                    scope.$parent.vm.ticket_detail = null;
                    scope.$parent.vm.ticket_clicked = false;
                    $(elem).hide("fold", 500);
                    $(scope.reduceItem).removeClass('col-md-' + scope.sizeReducedItem, 500);
                };
                $(elem).css('display', 'none');
            }
        };
    };

    var Notify = function (rootScope) {
        return {
            link: function (scope, elem, attrs, ctrl) {
                rootScope.$on('notify', function (event, data) {
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: data.title,
                        // (string | mandatory) the text inside the notification
                        text: data.description,
                        image: data.image || '',
                        class_name: data.class || '',
                        sticky: false,
                        // (int | optional) the time you want it to be alive for before fading out
                        time: 15000
                    });
                });
            }
        };
    };

    var CalculateWithBoard = function (rootScope, timeout) {
        return {
            link: function () {
                rootScope.$on('board-loaded', function () {
                    var calculateWidth = function () {
                        var list_width = 0;
                        var total_columns = $('.column').length;
                        list_width = $('.column').width() * total_columns;
                        list_width += 2 * total_columns;
                        //Set the area with the summatory of the cols width
                        $('.board-area').width(list_width);
                    };
                    timeout(calculateWidth, 0);
                });
            }
        };
    };

    var commentFlow = function (rootScope) {
        return {
            restrict: 'A',
            link: function (scope, elem, attrs, ctrl) {
                var txt = $(elem).find('textarea');
                var btn = $(elem).find('button');

                var restore = function () {
                    txt.attr('rows', 1);
                    txt.val('');
                    btn.hide();
                };

                $(txt).on('focus', function (e) {
                    txt.attr('rows', 5);
                    btn.show();
                }).on('blur', function (e) {
                    var rt = $(e.relatedTarget);
                    if (rt.attr('id') !== 'add-comment') {
                        restore();
                    }
                });

                rootScope.$on('comment_saved', function (params) {
                    restore();
                });
            }
        };
    };

    ImageFunction.$inject = ['$q'];
    InlineEdit.$inject = ['$timeout'];
    Notify.$inject = ['$rootScope'];
    commentFlow.$inject = ['$rootScope'];
    CalculateWithBoard.$inject = ['$rootScope', '$timeout'];
    TicketDetailView.$inject = ['Conf'];

    angular.module('Coati.Directives', ['Coati.Config'])
        .directive('image', ImageFunction)
        .directive('chart', Chart)
        .directive('onEsc', OnEscape)
        .directive('onEnter', OnEnter)
        .directive('inlineEdit', InlineEdit)
        .directive('ticketDetailView', TicketDetailView)
        .directive('notify', Notify)
        .directive('prepareBoard', CalculateWithBoard)
        .directive('commentFlow', commentFlow);


}(angular));