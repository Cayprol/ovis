odoo.define('ovis.framework', function (require){
"use strict";
var core = require('web.core');

function ReloadView(parent, action) {
	console.log("ReloadView");
	var controller = parent.getCurrentController();
	console.log("ReloadView controller");
	if (controller && controller.widget) {
		console.log("ReloadView widget");
		controller.widget.reload();
		console.log("ReloadView widget reload");
	}

}
core.action_registry.add("reload_view", ReloadView);

});