$(document).ready(function(){
    $('#save_tab').click(function(){
        $('#save_container').css("display","block");
        $('#find_container').css("display","none");
        $('#save_tab').attr("class","active");
        $('#find_tab').attr("class","");
    });
    $('#find_tab').click(function(){
        $('#find_container').css("display","block");
        $('#save_container').css("display","none");
        $('#find_tab').attr("class","active");
        $('#save_tab').attr("class","");
    });
});


function find_recipe(){

};


function save_url(){
    var url = $("#url").val();
};