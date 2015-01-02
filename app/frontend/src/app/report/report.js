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
            SprintService.all(project_id).then(function (sprints) {
                vm.sprints = sprints;
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
                    tooltip: {
                        useHTML: true,
                        headerFormat: '<span style="color:#ff0000;font-size: 10px">{point.key}</span><br/>',
                        formatter: function () {
                            if (this.series.name == 'Remaining') {
                                var tickets = chart_data.tickets_per_day[this.point.index];
                                var ul = $('<ul />');
                                angular.forEach(tickets, function (val, key) {
                                    if(val.indexOf('-') === 0){
                                        val = '<span style="color:#1dff41">' + val + '</span>';
                                    }else{
                                        val = '<span style="color:#ff0000">' + val + '</span>';
                                    }
                                    var li = $('<li />').html(val);
                                    ul.append(li);
                                });
                                var div = $('<div />');
                                var points = $('<p />').html('<b>Points</b>:' + this.y);
                                div.append(points);
                                if(tickets.length > 0) {
                                    var p = $('<p />').html('<b>Tickets</b>');
                                    div.append(p);
                                    div.append(ul);
                                }
                                return div.get(0).outerHTML;
                            }else{
                                return 'Points:' + this.y;
                            }
                        }
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
