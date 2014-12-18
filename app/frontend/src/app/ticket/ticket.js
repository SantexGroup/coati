(function (angular) {

    var TicketFormController = function (modalInstance, conf, TicketService, SprintService, item) {
        var vm = this;

        vm.form = {};
        vm.types = conf.TICKET_TYPES;

        if (item.ticket) {
            SprintService.query(item.project).then(function (sprints) {
                vm.sprints = sprints;
                TicketService.get(item.ticket).then(function (tkt) {
                    vm.ticket = tkt;
                    vm.labels = item.ticket.labels || [];
                });
            });
        } else {
            SprintService.query(item.project).then(function (sprints) {
                vm.sprints = sprints;
                vm.ticket = {};
                vm.labels = [];
            });
        }

        vm.save = function () {
            if (vm.form.ticket_form.$valid) {
                vm.ticket.labels = [];
                vm.labels.forEach(function (item) {
                    vm.ticket.labels.push(item.text);
                });

                if (vm.ticket.sprint) {
                    vm.ticket.sprint.pk = vm.ticket.sprint._id.$oid;
                }

                if (item.ticket) {
                    TicketService.update(vm.ticket._id.$oid, vm.ticket).then(function (tkt) {
                        modalInstance.close();
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                } else {
                    TicketService.save(item.project, vm.ticket).then(function (tkt) {
                        modalInstance.close();
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                }
            } else {
                vm.submitted = true;
            }
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    var TicketDeleteController = function (modalInstance, TicketService, item) {
        var vm = this;
        vm.ticket = item;
        vm.erase = function () {
            TicketService.delete_ticket(vm.ticket.pk).then(function () {
                modalInstance.close('delete');
            });
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };

    };

    var TicketDetailController = function (rootScope, modalInstance, conf, TicketService, item) {
        var vm = this;

        var getComments = function (ticket_id) {
            TicketService.get_comments(ticket_id).then(function (comments) {
                vm.comments = comments;
            });
        };

        TicketService.get(item.ticket_id).then(function (tkt) {
            vm.ticket = tkt;

            getComments(tkt._id.$oid);

            angular.forEach(conf.TICKET_TYPES, function (val, key) {
                if (val.value === vm.ticket.type) {
                    vm.type = val.name;
                    return;
                }
            });
        });

        vm.project = item.project;


        vm.add_new_comment = function (e) {
            if (vm.comment.length > 0) {
                var comment = {'comment': vm.comment};
                TicketService.add_comment(vm.ticket._id.$oid, comment).then(function (tkt) {
                    rootScope.$broadcast('comment_saved');
                    vm.comments.unshift(tkt);
                });
            }
            e.stopPropagation();
        };

        vm.close = function () {
            modalInstance.dismiss('cancelled');
        };

    };

    TicketDetailController.$inject = ['$rootScope','$modalInstance', 'Conf', 'TicketService', 'item'];
    TicketFormController.$inject = ['$modalInstance', 'Conf', 'TicketService', 'SprintService', 'item'];
    TicketDeleteController.$inject = ['$modalInstance', 'TicketService', 'item'];

    angular.module('Coati.Ticket', ['ui.router', 'ngTagsInput',
        'Coati.Config',
        'Coati.Directives',
        'Coati.Services.Ticket',
        'Coati.Services.Sprint'])
        .controller('TicketFormController', TicketFormController)
        .controller('TicketDeleteController', TicketDeleteController)
        .controller('TicketDetailController', TicketDetailController);


}(angular));
