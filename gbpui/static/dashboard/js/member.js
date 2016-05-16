member = {
  user_decided_length: false,
  user_volume_size: false,
  groups_selected: [],
  groups_available: [],

  /*
   * Gets the html select element associated with a given
   * group id for group_id.
   **/
  get_group_element: function(group_id) {
    return $('li > label[for^="id_network_' + group_id + '"]');
  },

  /*
   * Initializes an associative array of lists of the current
   * groups.
   **/
  init_group_list: function () {
    member.groups_selected = [];
    member.groups_available = [];
    $(this.get_group_element("")).each(function () {
      var $this = $(this);
      var $input = $this.children("input");
      var name = horizon.escape_html($this.text().replace(/^\s+/, ""));
      var group_property = {
        "name": name,
        "id": $input.attr("id"),
        "value": $input.attr("value")
      };
      if ($input.is(":checked")) {
        member.groups_selected.push(group_property);
      } else {
        member.groups_available.push(group_property);
      }
    });
  },

  /*
   * Generates the HTML structure for a group that will be displayed
   * as a list item in the group list.
   **/
  generate_group_element: function(name, id, value) {
    var $li = $('<li>');
    $li.attr('name', value).html(name + '<strong></strong><a href="#" class="btn btn-primary"></a>');
    return $li;
  },

  /*
   * Generates the HTML structure for the group List.
   **/
  generate_grouplist_html: function() {
    var self = this;
    var available_group = $("#available_group");
    var selected_group = $("#selected_network");
    var reset_unselected_group_fixed_ip = function(){
       ptg = $("#fixed_ip").attr("data-ptg")
       if($("ul#available_group li[name^='"+ ptg +"']").length > 0){
         $("ul#available_group li[name^='"+ ptg +"']").css("background-color", "");
         $("#fixed_ip_div").hide()
       }
    };
    var updateForm = function() {
      var groupListId = $("#groupListId");
      var lists = groupListId.find("li").attr('data-index',100);
      var active_groups = $("#selected_network > li").map(function(){
        return $(this).attr("name");
      });
      groupListId.find("input:checkbox").removeAttr('checked');
      active_groups.each(function(index, value){
        groupListId.find("input:checkbox[value^='" + value + "']")
          .prop('checked', true)
          .parents("li").attr('data-index',index);
      });
      groupListId.find("ul").html(
        lists.sort(function(a,b){
          if( $(a).data("index") < $(b).data("index")) { return -1; }
          if( $(a).data("index") > $(b).data("index")) { return 1; }
          return 0;
        })
      );
      reset_unselected_group_fixed_ip()
    };

    $("#groupListSortContainer").show();
    $("#groupListIdContainer").hide();
    self.init_group_list();
    // Make sure we don't duplicate the groups in the list
    available_group.empty();
    $.each(self.groups_available, function(index, value){
      available_group.append(self.generate_group_element(value.name, value.id, value.value));
    });
    // Make sure we don't duplicate the groups in the list
    selected_group.empty();
    $.each(self.groups_selected, function(index, value){
      selected_group.append(self.generate_group_element(value.name, value.id, value.value));
    });

    $(".networklist > li > a.btn").click(function(e){
      var $this = $(this);
      e.preventDefault();
      e.stopPropagation();
      if($this.parents("ul#available_group").length > 0) {
        $this.parent().appendTo(selected_group);
      } else if ($this.parents("ul#selected_network").length > 0) {
        $this.parent().appendTo(available_group);
      }
      updateForm();
    });
    if ($("#groupListId > div.form-group.error").length > 0) {
      var errortext = $("#groupListId > div.form-group.error span.help-block").text();
      $("#selected_group_label").before($('<div class="dynamic-error">').html(errortext));
    }
    $(".networklist").sortable({
      connectWith: "ul.networklist",
      placeholder: "ui-state-highlight",
      distance: 5,
      start:function(e,info){
        selected_group.addClass("dragging");
      },
      stop:function(e,info){
        selected_group.removeClass("dragging");
        updateForm();
      }
    }).disableSelection();
  },

  allow_fixed_ip: function(selected_group){
      fixed_ip = ""
      $("#fixed_ip").val("")
      $("#errors").text("")
      $("#fixed_ip_div").show()
      ptg = $(selected_group).attr('name')
      $(selected_group).siblings().css( "background-color", "");
      $(selected_group).css('background-color', '#e6e6e6');
      selected_element = $(".multiple-checkbox #id_network li input[value^='"+ ptg +"']");
      value = selected_element.val();
      values = value.split(':');
      group = $(selected_group).text()
      group = group.split("(")
      $("#group").text(group[0])
      subnets = values[1].split(";")
      $('#subnets_table tbody').empty();
      for (index=0; index < subnets.length; index++){
        subnet_details = subnets[index].split(",")
        row = '<tr><td>'+subnet_details[0]+'</td><td>'+
              subnet_details[1] +'</td><td>' + subnet_details[2]+'</td>';
        $('#subnets_table tbody').append(row);
      }
      $("#fixed_ip").attr("data-ptg", values[0]);
      $("#fixed_ip").attr("data-subnet", values[1])
      if (values.length == 3)
        $("#fixed_ip").val(values[2]);
  },
  associate_fixed_ip: function(){
      ptg = $("#fixed_ip").attr("data-ptg")
      subnet = $("#fixed_ip").attr("data-subnet")
      fixed_ip = $("#fixed_ip").val()
      if (!fixed_ip || 0 === fixed_ip.length ){
        $("#errors").text("Enter valid IP address")
        return
      }
      $.ajax({
        url: 'check_ip_availability',
        data: "fixed_ip="+fixed_ip+"&subnets="+subnet,
        method: 'get',
        success: function(response) {
          if(response.inuse){
            horizon.alert('success', "IP address '" + fixed_ip +"' is available.")
            value = ptg + ":" + subnet + ":" + fixed_ip
            selected_element = $(".multiple-checkbox #id_network li input[value^='"+ ptg +"']");
            selected_element.val(value)
            if(fixed_ip){
              $("#selected_network li[name^='"+ ptg +"'] strong").text(" ( "+fixed_ip + " )")
            }
            else{
              $("#selected_network li[name^='"+ ptg +"'] strong").text("")
            }
            $("ul#selected_network li[name^='"+ ptg +"']").css("background-color", "");
            $("#fixed_ip_div").hide()
          }
          else{
            $("#errors").text(response.error)
          }
        },
        error: function(response) {
          $("#errors").text(response)
        }
      });
  },
  disassociate_fixed_ip: function(){
    ptg = $("#fixed_ip").attr("data-ptg")
    subnet = $("#fixed_ip").attr("data-subnet")
    value = ptg + ":" + subnet
    selected_element = $(".multiple-checkbox #id_network li input[value^='"+ ptg +"']");
    selected_element.val(value)
    $("#selected_network li[name^='"+ ptg +"'] strong").text("")
    $("#fixed_ip_div").hide()
    $("ul#selected_network li").css("background-color", "");
  },
  groups_init: function() {
    // Initialise the drag and drop group list
    member.generate_grouplist_html();

    // allocate fixed ip
    $(document).on('click', "ul#selected_network li", function(){
      member.allow_fixed_ip(this);
    });

    $("#set_ip_button").click(function(){
      member.associate_fixed_ip();
    });

    $("#remove").click(function(){
      member.disassociate_fixed_ip()
    });
  }
};
