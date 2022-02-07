
let project = null;
let execution = null;

$(document).ready(function() {
    project = projectName;
    execution = executionName;
    fillInBreadcrumb(project, execution);
    if(project == null) {
        $('#reportTable thead tr').prepend('<th>Project</th>')
    }
    loadTable();
})

function loadTable() {
    let lastDays = getLastDaysValue();
    xhr.get('/api/report/get-reports', {project, execution, lastDays}, data => {
        $('#reportTable tbody').html('');
        for(report in data) {
            ReportDashboardMain.loadReport(data[report]);
        }
    })
}

const ReportDashboardMain = new function(){

    this.loadReport = function(report) {
        let executionName = report.execution;
        if(executionName == 'all') {
            executionName = 'all tests'
        }
        let reportRow = $(`
            <tr project="${report.project}" execution="${report.execution}" timestamp="${report.timestamp}">
                <td><a class="link-without-underline"
                    href="${Main.URLS.reportDashboard(report.project, report.execution)}">${executionName}</a></td>
                <td class="browsers">${report.report.params.browsers.map(b => b.name).join(', ')}</td>
                <td class="environments">${report.report.params.environments.join(', ')}</td>
                <td class="started">${Main.Utils.getDateTimeFromTimestamp(report.timestamp)}</td>
                <td class="duration">${Main.Utils.secondsToReadableString(report.report.net_elapsed_time)}</td>
                <td>${report.report.total_tests}</td>
                <td><div class="progress"></div></td>
                <td class="menu-buttons">
                    <a class="link-without-underline" href="${Main.URLS.executionReport(report.project, report.execution, report.timestamp)}">
                        <span class="glyphicon glyphicon-new-window" aria-hidden="true"></span>
                    </a>
                    <i class="glyphicon glyphicon-trash cursor-pointer" style="display: none;"
                        onclick="event.stopPropagation(); ReportDashboardMain.deleteExecutionTimestampConfirm(this)"></i>
                    <i class="fa fa-cog fa-spin spinner" style="display: none;"></i>
                    <i class="glyphicon glyphicon-pause cursor-pointer" style="display: none;"></i>
                </td>
	        </tr>`);

        if(project == null) {
            reportRow.prepend(`<td><a class="link-without-underline"
                    href="${Main.URLS.reportDashboard(report.project)}">${report.project}</a></td>`)
        }

        $('#reportTable tbody').append(reportRow)

        this.updateRow(reportRow, report.project, report.execution, report.timestamp, report.report)
    }

    this.updateRow = function(row, project, execution, timestamp, report) {

        let _updateRow = function(row, report) {
            let results = Object.keys(report.totals_by_result).sort();
            let container = row.find('div.progress');
            results.forEach(result => {
                if(!Main.ReportUtils.hasProgressBarForResult(container, result)) {
                    Main.ReportUtils.createProgressBars(container, [result])
                }
                let percentage = report.totals_by_result[result] * 100 / report.total_tests;
                Main.ReportUtils.animateProgressBar(container, result, percentage, report.totals_by_result[result]);
            });
            if(!('pending' in report.totals_by_result)) {
                Main.ReportUtils.animateProgressBar(container, 'pending', 0);
            }

            if(report.has_finished) {
                row.find('.browsers').html(report.params.browsers.map(b => b.name).join(', '));
                row.find('.environments').html(report.params.environments.join(', '));
                row.find('.duration').html(Main.Utils.secondsToReadableString(report.net_elapsed_time));
                row.find('.spinner').hide();
//                row.find('.glyphicon-pause').hide();
                if(Global.user.projectWeight >= Main.PermissionWeightsEnum.admin) {
                    row.find('.glyphicon-trash').show()
                }
            } else {
                // If an execution has taken more than 24 hs show the delete button
                // If Golem crashed during an execution and the report was not
                // generated, the execution will remain in a "running" state forever
                // TODO
                let dateStr = Main.Utils.getDateTimeFromTimestamp(timestamp);
                let unixTimestamp = Date.parse(dateStr);
                let elapsedHours = (Date.now() - unixTimestamp) / 1000 / 60 / 60;
                if(elapsedHours > 24) {
                    row.find('.glyphicon-trash').show()
                }
//                row.find('.glyphicon-pause').show();
                row.find('.spinner').show();
                setTimeout(ReportDashboardMain.updateRow, 3000, row, project, execution, timestamp)
            }
        }

        if(report == undefined) {
            xhr.get('/api/report/execution', {project, execution, timestamp}, report => {
                _updateRow(row, report)
            })
        } else {
            _updateRow(row, report)
        }
    }

    this.deleteExecutionTimestampConfirm = function(elem) {
        let row = $(elem).closest('tr');
        let project = row.attr('project');
        let execution = row.attr('execution');
        let timestamp = row.attr('timestamp');
        let message = `<span style="word-break: break-all">Are you sure you want to delete this execution? This action cannot be undone.</span>`;
        let callback = function() {
            ReportDashboardMain.deleteExecutionTimestamp(row, project, execution, timestamp);
        }
        Main.Utils.displayConfirmModal('Delete', message, callback);
    }

    this.deleteExecutionTimestamp = function(row, project, execution, timestamp){
        xhr.delete('/api/report/execution/timestamp', {project, execution, timestamp}, errors => {
            if(errors.length) {
                errors.forEach(error => Main.Utils.toast('error', error, 3000));
            } else {
                row.remove();
                Main.Utils.toast('info', 'Execution deleted', 2000)
            }
        });
        return false
    }
}

function fillInBreadcrumb(project, execution) {
    if(project != null) {
        if(execution == null) {
            $("#breadcrumb").html(
                `<a class="link-without-underline" href="/report/">All Projects</a> > ${project}`)
        }
        if(execution != null) {
            $("#breadcrumb").html(
                `<a class="link-without-underline" href="/report/">All Projects</a> >
                <a class="link-without-underline" href="/report/${project}/">${project}</a> > ${execution}`)
        }
    }
}

function getLastDaysValue() {
    return $("#lastDaysSelector").val()
}