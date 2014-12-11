(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.reports', {
            url: 'reports',
            views: {
                "project-reports": {
                    controller: 'ProjectCtrlReports',
                    controllerAs: 'vm',
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

    var ProjectCtrlReports = function (state, SprintService) {
        var vm = this;
        vm.is_not_started = false;

        var getSprints = function (project_id) {
            SprintService.query(project_id).then(function (sprints) {
                vm.sprints = sprints;
            });
        };

        var getSprintReport = function (sprint_id) {
            SprintService.get_chart(sprint_id).then(function (chart_data) {
                vm.chartData = {
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
                        plotLines: [
                            {
                                value: 0,
                                width: 1,
                                color: '#808080'
                            }
                        ]
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

        vm.getReport = function () {
            if (vm.sprint_selected && vm.sprint_selected.started) {
                getSprintReport(vm.sprint_selected._id.$oid);
            }else{
                if(vm.sprint_selected) {
                    vm.is_not_started = true;
                }else{
                    vm.is_not_started = false;
                }
                vm.chartData = null;
            }
        };

        getSprints(state.params.project_pk);

    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlReports.$inject = ['$state', 'SprintService'];

    angular.module('Coati.Report', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('ProjectCtrlReports', ProjectCtrlReports);

}(angular));
