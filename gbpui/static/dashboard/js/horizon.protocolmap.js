 $(function(){
        protocol_port_map = {'HTTP':80,'HTTPS':443,'SMTP':25,'DNS':53,'FTP':21 };
        $('#id_protocol').on('change',function(){
            if(protocol_port_map[$('#id_protocol>option:selected').text()] != undefined){
                port = protocol_port_map[$('#id_protocol>option:selected').text()]
                $('#id_port_range').val(port).attr('readonly', true)
            }
            else{
                $('#id_port_range').val('').attr('readonly', false);
            }
        });
});
