

window.onload = function () {
	let resultDiv = $("[data='test-result']");
	resultDiv.append(' ' + Main.Utils.getResultIcon(resultDiv.html()));
}

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