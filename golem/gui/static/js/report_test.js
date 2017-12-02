


function setLogLevel(logLevel){
	if(logLevel == 'debug'){
		$("#debugLogLines").show();
		$("#infoLogLines").hide();
	}
	else if(logLevel == 'info'){
		$("#infoLogLines").show();
		$("#debugLogLines").hide();
	}
}