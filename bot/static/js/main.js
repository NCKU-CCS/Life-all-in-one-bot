jQuery(document).ready(function()
{
	$.ajax(
	{
		type: 'get',
		url : 'TextCloud/?format=json',
		success :function(data){
			console.log(data);
		},
		error : function(err){
			console.log(err);
		}
	});

});