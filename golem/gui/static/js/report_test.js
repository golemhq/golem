

function expandImg(e){
	$("#expandedScreenshot").attr('src', e.srcElement.src);
	$("#screenshotModal").modal('show');
}