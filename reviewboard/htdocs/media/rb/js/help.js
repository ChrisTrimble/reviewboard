var kb_shortcuts = '' ;
$(document).ready(function() {
	$(document).keyup(function(e) {
		var KeyID = (window.event) ? event.keyCode : e.keyCode;
		if (KeyID == 27) {
            $("#helpPopUp").remove();
		}
    });

	/* Populating Help (?) Box */
	kb_shortcuts += '<table id="kb_shortcuts">' ;
	for (var i = 0; i < gActions.length; i++) { 
		kb_shortcuts += '<tr>';
		kb_shortcuts += '<td width="100">' +  makeDisplayKeys(gActions[i].keys) + '</td>';
		kb_shortcuts += '<td width="25"></td>';
		kb_shortcuts += '<td width="150"><font class="help">'+ gActions[i].description +'</font></td>';
		kb_shortcuts += '</tr>';
	}
});

// Converts a String from abc to a, b, c -- More readable format.
function makeDisplayKeys(keys){
	var display_keys = "";
	for(i=0;i<keys.length;i++){
		if (i==0){
			display_keys += '<font class="yl help">'+keys.charAt(i)+'</font>';
		}else{
			display_keys += ", "+'<font class="yl help">'+keys.charAt(i)+'</font>';
		}		
	}
	return display_keys;
}

// Display Help Screen
function displayHelpScreen() {
	$("<div/>")
		.addClass("dlgOpacity")
    	.popUpDlg({
      		title: "Keyboard Shortcuts",
      		width: "30em",
      		data: kb_shortcuts,
      		box_id: "helpPopUp"
    });
}
    
