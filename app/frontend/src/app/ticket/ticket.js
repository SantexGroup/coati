(function (angular) {

    var onEnter = function (timeout, q, stateParams, state, modal, ProjectService) {

        var vm = this;
        timeout(function () {
            vm.project = stateParams.project_pk;

            var modalInstance = modal.open({
                backdrop: true,
                windowClass: 'right fade',
                resolve: {
                    item: function () {
                        var promise = q.defer();
                        ProjectService.get(vm.project).then(function (prj) {
                            promise.resolve({
                                'project': prj,
                                'ticket_id': stateParams.ticket_id
                            });
                        }, function () {
                            promise.reject('Error');
                        });
                        return promise.promise;
                    }
                },
                templateUrl: "ticket/ticket_detail_view.tpl.html",
                controller: 'TicketDetailController',
                controllerAs: 'vm',
                data: {
                    pageTitle: 'Ticket Detail'
                }
            });
            modalInstance.result.then(function () {
                state.go('^', {}, {reload: false});
            }, function () {
                state.go('^', {}, {reload: false});
            });
        });
    };

    var Config = function (stateProvider, tagsInputProvider) {
        stateProvider.state('project.closed_tickets', {
            url: '/archived-tickets',
            views: {
                "closed_tickets": {
                    controller: 'TicketArchivedController',
                    controllerAs: 'vm',
                    templateUrl: 'ticket/archived_tickets.tpl.html'
                }
            },
            tab_active: 'closed_tickets',
            data: {
                pageTitle: 'Archived Tickets'
            },
            reloadOnSearch: false,
            reload: true
        })
            .state('project.planning.ticket', {
                url: '/ticket/:ticket_id',
                onEnter: ['$timeout', '$q', '$stateParams', '$state', '$modal', 'ProjectService', onEnter],
                reload: true,
                tab_active: 'planning'
            }).state('project.board.ticket', {
                url: '/ticket/:ticket_id',
                onEnter: ['$timeout', '$q', '$stateParams', '$state', '$modal', 'ProjectService', onEnter],
                reload: true,
                tab_active: 'board'
            }).state('project.closed_tickets.ticket', {
                url: '/ticket/:ticket_id',
                onEnter: ['$timeout', '$q', '$stateParams', '$state', '$modal', 'ProjectService', onEnter],
                reload: true,
                tab_active: 'closed_tickets'
            });

        tagsInputProvider.setDefaults('autoComplete', {
            maxResultsToShow: 20,
            debounceDelay: 300
        });
    };

    var TicketFormController = function (log, modalInstance, conf, TicketService, SprintService, item) {
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
            SprintService.query(item.project._id.$oid).then(function (sprints) {
                vm.sprints = sprints;
                vm.ticket = {};
                vm.labels = [];
            });
        }

        vm.is_scrumm = function () {
            return item.project.project_type === "S";
        };

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
                    TicketService.update(item.project._id.$oid, vm.ticket._id.$oid, vm.ticket).then(function (tkt) {
                        modalInstance.close(tkt);
                    }, function (err) {
                        modalInstance.dismiss('error');
                        log.error(err);
                    });
                } else {
                    TicketService.save(item.project._id.$oid, vm.ticket).then(function (tkt) {
                        modalInstance.close(tkt);
                    }, function (err) {
                        modalInstance.dismiss('error');
                        log.error(err);
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

    var TicketDeleteController = function (modalInstance, TicketService, item, project) {
        var vm = this;
        vm.ticket = item;
        vm.erase = function () {
            TicketService.delete_ticket(project, vm.ticket.pk).then(function () {
                modalInstance.close('delete');
            });
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };

    };

    var TicketDetailController = function (rootScope, log, filter, tmo, modalInstance, conf, downloader, ProjectService, TicketService, SocketIO, item) {
        var vm = this;


        vm.files = [];
        vm.file_uploaded = 0;
        vm.members_filtered = [];
        vm.mentions = [];
        vm.types = conf.TICKET_TYPES;
        vm.ticket_dependencies = conf.TICKET_DEPENDENCIES;
        vm.no_editing = item.disabled || false;
        vm.related_collapsed = true;
        vm.user = rootScope.user;

        var getComments = function (ticket_id) {
            TicketService.get_comments(vm.project._id.$oid, ticket_id).then(function (comments) {
                vm.comments = comments;
            });
        };

        var getMembers = function () {
            ProjectService.get_members(vm.project._id.$oid).then(function (data) {
                vm.members = data;
            });
        };

        var getTicket = function (ticket_id) {
            return TicketService.get(vm.project._id.$oid, ticket_id).then(function (tkt) {
                vm.ticket = tkt;
                vm.labels = tkt.labels;
                getComments(tkt._id.$oid);
            }, function () {
                modalInstance.dismiss('error loading ticket');
            });
        };

        var do_upload = function (file) {
            file.upload = TicketService.upload_attachments(vm.project._id.$oid, vm.ticket._id.$oid, file,
                {'name': file.name, 'size': file.size, 'type': file.type})
                .progress(function (evt) {
                    //console.log('progress: ' + parseInt(100.0 * evt.loaded / evt.total, 10) + '% file :'+ evt.config.file.name);
                    evt.config.file.progress = parseInt(100.0 * evt.loaded / evt.total, 10);
                }).success(function (att) {
                    vm.ticket.files.push(att);
                    vm.file_uploaded += 1;
                    if (vm.file_uploaded == vm.files.length) {
                        vm.files = [];
                    }
                });
        };

        vm.project = item.project;
        getTicket(item.ticket_id);
        getMembers();

        vm.is_scrumm = function () {
            return vm.project.project_type === "S";
        };

        vm.update_comment = function(c){
            c.comment = c.comment_temp;
            TicketService.update_comment(vm.project._id.$oid, vm.ticket._id.$oid, c._id.$oid, c).then(function(comment){
                for(var i = 0; i<vm.comments.length;i++){
                    if(vm.comments[i]._id.$oid == c._id.$oid){
                        vm.comments[i] = comment;
                        vm.cancel_edit_comment(vm.comments[i]);
                        break;
                    }
                }
            });
        };

        vm.delete_comment = function(c){
            TicketService.delete_comment(vm.project._id.$oid, vm.ticket._id.$oid, c._id.$oid).then(function(){
                for(var i = 0; i<vm.comments.length;i++){
                    if(vm.comments[i]._id.$oid == c._id.$oid){
                        vm.comments.splice(i,1);
                        break;
                    }
                }
            });
        };

        vm.edit_comment = function(c){
            c.editable = true;
            c.comment_temp = c.comment;
        };

        vm.cancel_edit_comment = function(c){
            c.editable = false;
            c.comment_temp = '';
        };

        vm.show = function (form) {
            if (!vm.no_editing) {
                form.$show();
            }
        };

        vm.searchTickets = function (q) {
            return TicketService.related_search(vm.project._id.$oid, q);
        };

        vm.prepareLabelsToDependencies = function (save) {
            vm.ticket.related_tickets_data = [];
            angular.forEach(vm.related_tickets, function (v, k) {
                vm.ticket.related_tickets_data.push({'value': v.value,
                    'type': vm.dependency_type});
            });
            if (save) {
                vm.saveTicket(vm.ticket).then(function () {
                    vm.cancelDependencyAdd();
                });
            }
        };
        vm.remove_related_ticket = function (rtkt) {
            TicketService.remove_related(vm.project._id.$oid, vm.ticket._id.$oid, rtkt._id.$oid).then(function () {
                getTicket(vm.ticket._id.$oid);
            });
        };

        vm.getDependencyType = function (type) {
            var value = _.result(_.findWhere(vm.ticket_dependencies, { 'value': type }), 'name');
            return value;
        };

        vm.cancelDependencyAdd = function () {
            vm.related_collapsed = true;
            vm.related_tickets = [];
            vm.dependency_type = null;
        };

        vm.saveTicket = function (ticket) {
            if (ticket) {
                ticket.sprint = undefined;
                return TicketService.update(vm.project._id.$oid, ticket._id.$oid, ticket).then(function (tkt) {
                    vm.ticket = tkt;
                    rootScope.$broadcast('savedTicket', tkt);
                });
            }
        };

        vm.searchMember = function (term) {
            vm.members_filtered = filter('filter')(vm.members, term);
        };

        vm.getMemberText = function (item) {
            // note item.label is sent when the typedText wasn't found
            var name = item.member.first_name ? item.member.first_name + ' ' + item.member.last_name : item.member.email;
            return '<span class="badge bg-info" data-token="' + item.member._id.$oid + '" contenteditable="false">@' + name + '</span>';
        };

        vm.removeFileFromQueue = function (f) {
            _.pull(vm.files, f);
        };

        vm.delete_file = function (f) {
            TicketService.delete_attachment(vm.project._id.$oid, vm.ticket._id.$oid, f._id.$oid).then(function () {
                _.pull(vm.ticket.files, f);
            });
        };


        vm.download = function (f) {
            downloader.download_file(f.name, f.type, f.data);
        };


        vm.archive_restore_ticket = function (archive) {
            vm.ticket.closed = archive;
            TicketService.update(vm.project._id.$oid, vm.ticket._id.$oid, vm.ticket).then(function (tkt) {
                modalInstance.close();
                if(archive) {
                    rootScope.$broadcast('archivedTicket', vm.ticket);
                }else{
                    rootScope.$broadcast('restoredTicket', vm.ticket);
                }
            }, function (err) {
                modalInstance.dismiss('error');
            });
        };

        vm.assign_to_ticket = function (m) {
            TicketService.assign_member(vm.project._id.$oid, vm.ticket._id.$oid, m._id.$oid).then(function () {
                getTicket(vm.ticket._id.$oid).then(function () {
                    rootScope.$broadcast('savedTicket', vm.ticket);
                });
            });
        };

        vm.remove_from_ticket = function (m) {
            TicketService.remove_member(vm.project._id.$oid, vm.ticket._id.$oid, m._id.$oid).then(function () {
                getTicket(vm.ticket._id.$oid).then(function () {
                    rootScope.$broadcast('savedTicket', vm.ticket);
                });
            });
        };

        vm.checkTypeIcon = function (f) {
            var classes = {
                'icon-file-text': f.type === 'text/plain',
                'icon-file-image-o': (f.type.indexOf('image/') > -1),
                'icon-file-pdf-o': f.type === 'application/pdf',
                'icon-file-zip-o': f.type === 'application/zip',
                'icon-file-archive-o': f.type === 'application/x-rar',
                'icon-file-excel-o': (f.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || f.type === 'application/vnd.ms-excel'),
                'icon-file-word-o': (f.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || f.type === 'application/msword'),
                'icon-file-powerpoint-o': (f.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation' || f.type === 'application/vnd.ms-powerpoint'),
                'icon-file': f.type === '' || f.type === 'text/html'
            };
            return classes;
        };

        vm.process_comment = false;
        vm.add_new_comment = function (e) {
            if (vm.comment.length > 0 && !vm.process_comment) {
                vm.process_comment = true;
                tmo(function () {
                    var comment = {'comment': vm.comment, 'mentions': vm.mentions};
                    TicketService.add_comment(vm.project._id.$oid, vm.ticket._id.$oid, comment).then(function (tkt) {
                        rootScope.$broadcast('comment_saved');
                        vm.comments.unshift(tkt);
                        vm.process_comment = false;
                    });
                }, 500);
            }
            e.stopPropagation();
        };

        vm.close = function () {
            modalInstance.close('closed');
        };


        vm.confirm_upload = function () {
            angular.forEach(vm.files, function (f, k) {
                do_upload(f);
            });
        };

        vm.abort_upload = function (f) {
            f.upload.abort();
            f.aborted = true;
        };

        vm.prepareLabelsToSave = function (lbls, save) {
            vm.ticket.labels = [];
            angular.forEach(vm.labels, function (v, k) {
                vm.ticket.labels.push(v.text);
            });
            if (save) {
                vm.saveTicket(vm.ticket);
            }
        };

        SocketIO.on('update_ticket', function () {
            getTicket(item.ticket_id);
        });
        SocketIO.on('ticket_transition', function () {
            getTicket(item.ticket_id);
        });

    };

    var TicketArchivedController = function (rootScope, scope, modal, TicketService) {
        var vm = this;

        vm.project = scope.$parent.project;

        var getArchivedTickets = function (project_id) {
            vm.loading_tickets = true;
            TicketService.closed_tickets(project_id).then(function (tickets) {
                vm.tickets = tickets;
                vm.loading_tickets = false;
            });
        };

        vm.is_scrumm = function () {
            return vm.project.project_type === 'S';
        };


        vm.is_scrumm = function () {
            return vm.project.project_type === "S";
        };

        getArchivedTickets(vm.project._id.$oid);

        rootScope.$on('restoredTicket', function(evt, tkt){
            for(var i =0;i<vm.tickets.length;i++){
                if(vm.tickets[i]._id.$oid == tkt._id.$oid){
                    vm.tickets.splice(i, 1);
                }
            }
        });

    };

    Config.$inject = ['$stateProvider', 'tagsInputConfigProvider'];
    TicketArchivedController.$inject = ['$rootScope','$scope', '$modal', 'TicketService'];
    TicketDetailController.$inject = ['$rootScope', '$log', '$filter', '$timeout', '$modalInstance', 'Conf', '$file_download', 'ProjectService', 'TicketService', 'SocketIO', 'item'];
    TicketFormController.$inject = ['$log', '$modalInstance', 'Conf', 'TicketService', 'SprintService', 'item'];
    TicketDeleteController.$inject = ['$modalInstance', 'TicketService', 'item', 'project'];

    angular.module('Coati.Ticket', ['ui.router', 'ngTagsInput', 'xeditable', 'pascalprecht.translate',
        'angularFileUpload',
        'mentio',
        'Coati.Config',
        'Coati.SocketIO',
        'Coati.Helpers',
        'Coati.Directives',
        'Coati.Services.Project',
        'Coati.Services.Ticket',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('TicketFormController', TicketFormController)
        .controller('TicketDeleteController', TicketDeleteController)
        .controller('TicketArchivedController', TicketArchivedController)
        .controller('TicketDetailController', TicketDetailController);


}(angular));
