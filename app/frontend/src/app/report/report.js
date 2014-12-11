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

    var ProjectCtrlReports = function (scope, state, SprintService) {

        var getSprints = function (project_id) {
            SprintService.query(project_id).then(function (sprints) {
                scope.sprints = sprints;
            });
        };

        var getSprintReport = function (sprint_id) {
            SprintService.get_chart(sprint_id).then(function (chart_data) {
                scope.chartData = {
                    title: {
                        text: 'BurnDown Chart',
                        x: -20 //center
                    },
                    xAxis: {
                        categories: chart_data.dates
                    },
                    yAxis: {
                        title: {
                            text: 'Points'
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    series: [
                        {
                            name: 'Ideal',
                            data: chart_data.ideal
                        },
                        {
                            name: 'Remaining',
                            data: chart_data.points_remaining
                        }
                    ]

                };
            });
        };

        scope.getReport = function () {
            getSprintReport(scope.sprint_selected);
        };

        getSprints(state.params.project_pk);

    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlReports.$inject = ['$scope', '$state', 'SprintService'];

    angular.module('Coati.Report', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('ProjectCtrlReports', ProjectCtrlReports);

}(angular));
