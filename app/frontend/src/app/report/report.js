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

    var ProjectCtrlReports = function (scope, state, SprintService) {
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

            SprintService.get_chart(vm.project._id.$oid, sprint_id).then(function (chart_data) {
                vm.tickets = chart_data.all_tickets;
                vm.chartData = {
                    labels: chart_data.dates,
                    tickets: chart_data.tickets,
                    velocity: chart_data.velocity,
                    eta: chart_data.eta,
                    planned_points: chart_data.planned_points,
                    name: 'Burndown',
                    datasets: [
                        {
                            label: 'Ideal Planned',
                            data: chart_data.ideal_planned,
                            strokeColor: "rgba(46,159,12,1)",
                            pointColor: "rgba(129,244,143,1)"
                        },
                        {
                            label: 'Velocity Trend',
                            data: chart_data.ideal_real,
                            strokeColor: "rgba(194,28,253,1)",
                            pointColor: "rgba(226,173,251,1)"
                        },
                        {
                            label: 'Remaining Points',
                            strokeColor: "rgba(255,0,0, 1) ",
                            pointColor: "rgba(254,146,146,1)",
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
        vm.project = scope.$parent.project;
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
