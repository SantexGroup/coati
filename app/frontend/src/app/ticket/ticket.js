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

    var TicketDetailController = function (rootScope, filter, tmo, modalInstance, conf, downloader, ProjectService, TicketService, SocketIO, item) {
        var vm = this;

        vm.files = [];
        vm.file_uploaded = 0;
        vm.members_filtered = [];
        vm.mentions = [];

        vm.types = conf.TICKET_TYPES;

        var getComments = function (ticket_id) {
            TicketService.get_comments(ticket_id).then(function (comments) {
                vm.comments = comments;
            });
        };

        var getMembers = function () {
            ProjectService.get_members(vm.project._id.$oid).then(function (data) {
                vm.members = data;
            });
        };

        var getTicket = function (ticket_id) {
            TicketService.get(ticket_id).then(function (tkt) {
                vm.ticket = tkt;
                vm.labels = tkt.labels;

                getComments(tkt._id.$oid);


            }, function () {
                modalInstance.dismiss('error loading ticket');
            });
        };

        var do_upload = function (file) {
            file.upload = TicketService.upload_attachments(vm.ticket._id.$oid, file,
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

        vm.saveTicket = function (ticket) {
            if (ticket) {
                ticket.sprint = undefined;
                TicketService.update(ticket._id.$oid, ticket).then(function (tkt) {
                    vm.ticket = tkt;
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
            TicketService.delete_attachment(vm.ticket._id.$oid, f._id.$oid).then(function () {
                _.pull(vm.ticket.files, f);
            });
        };


        vm.download = function (f) {
            downloader.download_file(f.name, f.type, f.data);
        };

        vm.checkMember = function (m) {
            if (vm.ticket !== undefined) {
                return _.find(vm.ticket.assigned_to, function (obj) {
                    var valid = obj._id.$oid === m._id.$oid;
                    m.checked = valid;
                    return valid;
                });
            }
        };

        vm.assign_to_ticket = function (m) {
            if (m.checked) {
                TicketService.assign_member(vm.ticket._id.$oid, m._id.$oid).then(function () {
                    getTicket(vm.ticket._id.$oid);
                }, function () {
                    m.checked = false;
                });
            } else {
                TicketService.remove_member(vm.ticket._id.$oid, m._id.$oid).then(function () {
                    getTicket(vm.ticket._id.$oid);
                }, function () {
                    m.checked = true;
                });
            }
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
                    TicketService.add_comment(vm.ticket._id.$oid, comment).then(function (tkt) {
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

    TicketDetailController.$inject = ['$rootScope', '$filter', '$timeout', '$modalInstance', 'Conf', '$file_download', 'ProjectService', 'TicketService', 'SocketIO', 'item'];
    TicketFormController.$inject = ['$modalInstance', 'Conf', 'TicketService', 'SprintService', 'item'];
    TicketDeleteController.$inject = ['$modalInstance', 'TicketService', 'item'];

    angular.module('Coati.Ticket', ['ui.router', 'ngTagsInput', 'angularFileUpload', 'mentio', 'pascalprecht.translate',
        'Coati.Config',
        'Coati.SocketIO',
        'Coati.Helpers',
        'Coati.Directives',
        'Coati.Services.Project',
        'Coati.Services.Ticket',
        'Coati.Services.Sprint'])
        .controller('TicketFormController', TicketFormController)
        .controller('TicketDeleteController', TicketDeleteController)
        .controller('TicketDetailController', TicketDetailController);


}(angular));
