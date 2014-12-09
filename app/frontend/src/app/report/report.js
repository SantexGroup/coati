(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.reports', {
            url: 'reports',
            views: {
                "project-reports": {
                    controller: 'ProjectCtrlReports',
                    templateUrl: 'report/reports.tpl.html'
                }
            },
            tab_active: 'reports',
            data: {
                pageTitle: 'Project Reports'
            },
            reload: true
        });
    };

    var ProjectCtrlReports = function (scope, state) {

    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlReports.$inject = ['$scope', '$state'];

    angular.module('Coati.Report', ['ui.router',
        'Coati.Directives'])
        .config(Config)
        .controller('ProjectCtrlReports', ProjectCtrlReports);

}(angular));
