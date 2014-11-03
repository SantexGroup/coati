angular.module('templates-app', ['extras/404.tpl.html', 'home/home.tpl.html', 'project/board.tpl.html', 'project/overview.tpl.html', 'project/project.tpl.html', 'project/reports.tpl.html', 'project/settings.tpl.html', 'user/user.tpl.html']);

angular.module("extras/404.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("extras/404.tpl.html",
    "<section class=\"error-wrapper\" change-body>\n" +
    "    <i class=\"icon-404\"></i>\n" +
    "\n" +
    "    <h1>404</h1>\n" +
    "\n" +
    "    <h2>page not found</h2>\n" +
    "\n" +
    "    <p class=\"page-404\">Something went wrong or that page doesn’t exist yet. <a\n" +
    "            href=\"/home\">Return Home</a></p>\n" +
    "</section>");
}]);

angular.module("home/home.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("home/home.tpl.html",
    "<div class=\"row\" style=\"margin-bottom:10px;\">\n" +
    "    <div class=\"col-lg-12\">\n" +
    "        <button type=\"button\" class=\"btn btn-primary\"><i\n" +
    "                class=\"icon-tasks\"></i> New Project\n" +
    "        </button>\n" +
    "    </div>\n" +
    "</div>\n" +
    "<div class=\"row\">\n" +
    "    <div class=\"col-lg-12\">\n" +
    "        <h4>Projects</h4>\n" +
    "\n" +
    "        <p data-ng-show=\"projects.length < 1\">You don't have Projects created\n" +
    "            yet!</p>\n" +
    "\n" +
    "        <!--widget start-->\n" +
    "        <aside class=\"profile-nav alt blue-border col-lg-3\"\n" +
    "               style=\"margin-right: 5px\"\n" +
    "               ng-repeat=\"item in projects track by item._id.$oid\"\n" +
    "               data-index=\"<[ $index ]>\">\n" +
    "            <section class=\"panel\">\n" +
    "                <div class=\"user-heading alt blue-bg\">\n" +
    "                    <h1>\n" +
    "                        <a href=\"/project/<[ item.slug ]>/\"><[\n" +
    "                            item.name\n" +
    "                            ]></a>\n" +
    "                    </h1>\n" +
    "                </div>\n" +
    "                <p><[ item.description ]></p>\n" +
    "                <ul class=\"nav nav-pills nav-stacked\">\n" +
    "                    <li>\n" +
    "                        <span class=\"label\"\n" +
    "                              data-ng-class=\"{true: 'label-sucess', false: 'label-danger'}[item.active]\"></span>\n" +
    "                    </li>\n" +
    "                </ul>\n" +
    "\n" +
    "            </section>\n" +
    "        </aside>\n" +
    "        <!--widget end-->\n" +
    "    </div>\n" +
    "</div>");
}]);

angular.module("project/board.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("project/board.tpl.html",
    "<h2>Board view</h2>");
}]);

angular.module("project/overview.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("project/overview.tpl.html",
    "<h2><[ project.name ]></h2>");
}]);

angular.module("project/project.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("project/project.tpl.html",
    "<div class=\"row\">\n" +
    "    <div class=\"col-lg-12\">\n" +
    "        <section class=\"panel\">\n" +
    "            <header class=\"panel-heading tab-bg-dark-navy-blue \">\n" +
    "                <ul class=\"nav nav-tabs\">\n" +
    "                    <li ng-class=\"{active:overview}\">\n" +
    "                        <a data-toggle=\"tab\" ng-click=\"switchView('project.overview');\">Overview</a>\n" +
    "                    </li>\n" +
    "                    <li ng-class=\"{active:board}\">\n" +
    "                        <a data-toggle=\"tab\"  ng-click=\"switchView('project.board');\">Board</a>\n" +
    "                    </li>\n" +
    "                    <li ng-class=\"{active:reports}\">\n" +
    "                        <a data-toggle=\"tab\" ng-click=\"switchView('project.reports');\">Reports</a>\n" +
    "                    </li>\n" +
    "                    <li ng-class=\"{active:settings}\">\n" +
    "                        <a data-toggle=\"tab\" ng-click=\"switchView('project.settings');\">Settings</a>\n" +
    "                    </li>\n" +
    "                </ul>\n" +
    "            </header>\n" +
    "            <div class=\"panel-body\">\n" +
    "                <div class=\"tab-content\">\n" +
    "                    <div id=\"overview\" ui-view=\"project-overview\"\n" +
    "                         class=\"tab-pane\" ng-class=\"{active:overview}\"></div>\n" +
    "                    <div id=\"board\" ui-view=\"project-board\" class=\"tab-pane\"\n" +
    "                         ng-class=\"{active:board}\">Board View\n" +
    "                    </div>\n" +
    "                    <div id=\"reports\" ui-view=\"project-reports\" class=\"tab-pane\"\n" +
    "                         ng-class=\"{active:reports}\">Reports\n" +
    "                    </div>\n" +
    "                    <div id=\"settings\" ui-view=\"project-settings\"\n" +
    "                         class=\"tab-pane\" ng-class=\"{active:settings}\">Settings\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "        </section>\n" +
    "    </div>\n" +
    "</div>");
}]);

angular.module("project/reports.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("project/reports.tpl.html",
    "<h2>Reports View</h2>");
}]);

angular.module("project/settings.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("project/settings.tpl.html",
    "<h2>Settings View</h2>");
}]);

angular.module("user/user.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("user/user.tpl.html",
    "<div class=\"col-lg-6\">\n" +
    "\n" +
    "    <section class=\"panel\">\n" +
    "\n" +
    "\n" +
    "        <header class=\"panel-heading\">\n" +
    "            User Profile\n" +
    "        </header>\n" +
    "        <div class=\"panel-body\">\n" +
    "            <form class=\"form-horizontal\" name=\"form\">\n" +
    "\n" +
    "                <div class=\"alert alert-block alert-danger fade in\"\n" +
    "                     data-ng-repeat=\"alert in alerts\">\n" +
    "                    <button data-dismiss=\"alert\"\n" +
    "                            data-ng-click=\"closeAlert($index)\"\n" +
    "                            class=\"close close-sm\" type=\"button\">\n" +
    "                        <i class=\"icon-remove\"></i>\n" +
    "                    </button>\n" +
    "                    <[ alert.msg ]>\n" +
    "                </div>\n" +
    "\n" +
    "                <div class=\"form-group\">\n" +
    "                    <label class=\"col-lg-2 col-sm-2 control-label\">Image</label>\n" +
    "\n" +
    "                    <div class=\"col-lg-10\">\n" +
    "                        <input type=\"file\" accept=\"image/*\"\n" +
    "                               data-ng-model=\"picture\"\n" +
    "                               image=\"image\"\n" +
    "                               resize-max-height=\"120\"\n" +
    "                               resize-max-width=\"120\"\n" +
    "                               resize-quality=\"1\"/>\n" +
    "                        <img data-ng-show=\"image\"\n" +
    "                             data-ng-src=\"<[ image.resized.dataURL ]>\"\n" +
    "                             type=\"<[ image.file.type ]>\" width=\"120\"/>\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "                <div class=\"form-group\">\n" +
    "                    <label class=\"col-lg-2 col-sm-2 control-label\">First\n" +
    "                        Name</label>\n" +
    "\n" +
    "                    <div class=\"col-lg-10\">\n" +
    "                        <input class=\"form-control\" autocomplete=\"off\"\n" +
    "                               placeholder=\"First Name\"\n" +
    "                               data-ng-model=\"user.first_name\"\n" +
    "                               name=\"first_name\" type=\"text\">\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "                <div class=\"form-group\">\n" +
    "                    <label class=\"col-lg-2 col-sm-2 control-label\">Last\n" +
    "                        Name</label>\n" +
    "\n" +
    "                    <div class=\"col-lg-10\">\n" +
    "                        <input class=\"form-control\" autocomplete=\"off\"\n" +
    "                               placeholder=\"Last Name\"\n" +
    "                               data-ng-model=\"user.last_name\"\n" +
    "                               name=\"last_name\" type=\"text\">\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "                <div class=\"form-group\">\n" +
    "                    <label class=\"col-lg-2 col-sm-2 control-label\">Username</label>\n" +
    "\n" +
    "                    <div class=\"col-lg-10\">\n" +
    "                        <input class=\"form-control\" autocomplete=\"off\"\n" +
    "                               placeholder=\"Username\"\n" +
    "                               data-ng-model=\"user.username\"\n" +
    "                               name=\"username\" type=\"text\">\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "                <div class=\"form-group\">\n" +
    "                    <label class=\"col-lg-2 col-sm-2 control-label\">Email</label>\n" +
    "\n" +
    "                    <div class=\"col-lg-10\">\n" +
    "                        <input class=\"form-control\" autocomplete=\"off\"\n" +
    "                               placeholder=\"E-Mail\" data-ng-model=\"user.email\"\n" +
    "                               name=\"email\" type=\"email\">\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "                <div class=\"form-group\">\n" +
    "                    <div class=\"col-lg-12\">\n" +
    "                        <button type=\"button\" class=\"btn btn-primary\"\n" +
    "                                data-ng-click=\"save(image, form);\">Submit\n" +
    "                        </button>\n" +
    "                        <a href=\"/home/\" type=\"button\" class=\"btn btn-danger\">Cancel\n" +
    "                        </a>\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "\n" +
    "            </form>\n" +
    "        </div>\n" +
    "    </section>\n" +
    "</div>");
}]);
