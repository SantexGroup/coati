(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.reports', {
            url: '/reports',
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
            SprintService.all(project_id).then(function (sprints) {
                vm.sprints = sprints;

                vm.sprint_selected = _.find(sprints, function(s){
                    return s.started && !s.finalized;
                });
                if(vm.sprint_selected){
                    vm.is_not_started = false;
                    getSprintReport(vm.sprint_selected._id.$oid);
                }

            });
        };

        vm.getSprintType = function(s){
            if(s.finalized){
                return 'Finalized Sprints';
            }else{
                return 'Current Sprints';
            }
        };

        var getSprintReport = function (sprint_id) {

            SprintService.get_chart(sprint_id).then(function (chart_data) {
                vm.tickets = chart_data.all_tickets;
                vm.chartData = {
                    title: {
                        text: 'BurnDown Chart',
                        x: -20 //center
                    },
                    xAxis: {
                        categories: chart_data.dates,
                        labels: {
                            overflow: 'justify'
                        }
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
                vm.is_not_started = false;
                getSprintReport(vm.sprint_selected._id.$oid);
            } else {
                if (vm.sprint_selected) {
                    vm.is_not_started = true;
                } else {
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
