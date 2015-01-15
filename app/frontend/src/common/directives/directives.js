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

    var ChartDraw = function () {
        return {
            restrict: 'E',
            template: '<canvas></canvas>',
            scope: {
                chartData: "=value"
            },
            transclude: true,
            replace: true,
            link: function (scope, element, attrs) {
                scope.$watch(function () {
                    return scope.chartData;
                }, function (value) {
                    var newSettings;
                    if (!value) {
                        $(element).empty();
                        return;
                    }
                    var ctx = element[0].getContext("2d");
                    var options = {
                        scaleShowGridLines : true,
                        scaleGridLineColor : "rgba(0,0,0,.05)",
                        scaleGridLineWidth : 1,
                        datasetFill : false,
                        responsive: true,
                        tooltipFontSize: 10,
                        // String - Tooltip font weight style
                        tooltipFontStyle: "normal",
                        // String - Tooltip label font colour
                        tooltipFontColor: "#fff",
                        // Number - Tooltip title font size in pixels
                        tooltipTitleFontSize: 12,
                        tooltipTemplate: "<%if (label){%><%=label%>: <%}%><%= math.round(value) %>",
                        legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].lineColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                    };

                    return new Chart(ctx).Line(scope.chartData, options);
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

                        //set same height of content column
                        $('.task-list').each(function () {
                            $(this).css('min-height', $(this).parent().parent().height());
                        });
                    };
                    timeout(calculateWidth, 0);
                });
            }
        };
    };

    var editableTagInput = function (editableDirectiveFactory) {
        return editableDirectiveFactory({
            directiveName: 'editableTags',
            inputTpl: '<div></div>',
            render: function () {
                this.parent.render.call(this);
                var tagIn = '<tags-input ng-model="$data" replace-spaces-with-dashes="false" placeholder="Add Label"></tags-input>';
                this.inputEl.before(tagIn);
                if (this.attrs.eStyle) {
                    this.inputEl.style = this.attrs.eStyle;
                }
            },
            autosubmit: function () {
                var self = this;
                self.inputEl.bind('change', function () {
                    self.scope.$apply(function () {
                        self.scope.$form.$submit();
                    });
                });
            }
        });
    };


    var contentEditable = function ($sce) {
        return {
            restrict: 'A', // only activate on element attribute
            require: '?ngModel', // get a hold of NgModelController
            link: function (scope, element, attrs, ngModel) {
                function read() {
                    var html = element.html();
                    // When we clear the content editable the browser leaves a <br> behind
                    // If strip-br attribute is provided then we strip this out
                    if (attrs.stripBr && html === '<br>') {
                        html = '';
                    }


                    if(attrs.mentions){

                        var spans = element.find('span');
                        scope.vm.mentions = [];
                        angular.forEach(spans, function(item, key){
                            scope.vm.mentions.push(item.getAttribute('data-token'));
                        });
                    }
                    console.log(html);
                    ngModel.$setViewValue(html);
                }

                if (!ngModel) {
                    return;
                } // do nothing if no ng-model

                // Specify how UI should be updated
                ngModel.$render = function () {
                    if (ngModel.$viewValue !== element.html()) {
                        element.html($sce.getTrustedHtml(ngModel.$viewValue || ''));
                    }
                };

                // Listen for change events to enable binding
                element.on('blur keyup change', function () {
                    scope.$apply(read);
                });

                scope.$on('comment_saved', function(){
                    element.empty();
                });

                read(); // initialize
            }
        };
    };


    var datepicker_fix = function () {
        return {
            restrict: 'EAC',
            require: 'ngModel',
            link: function (scope, element, attr, controller) {
                //remove the default formatter from the input directive to prevent conflict
                controller.$formatters.shift();
            }
        };
    };

    ImageFunction.$inject = ['$q'];
    contentEditable.$inject = ['$sce'];
    editableTagInput.$inject = ['editableDirectiveFactory'];
    CalculateWithBoard.$inject = ['$rootScope', '$timeout'];

    angular.module('Coati.Directives', ['Coati.Config'])
        .directive('image', ImageFunction)
        .directive('chart', ChartDraw)
        .directive('onEsc', OnEscape)
        .directive('onEnter', OnEnter)
        .directive('prepareBoard', CalculateWithBoard)
        .directive('editableTags', editableTagInput)
        .directive('datepickerPopup', datepicker_fix)
        .directive('contenteditable', contentEditable);


}(angular));