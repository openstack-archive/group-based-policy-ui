horizon.Node = {
  user_decided_length: false,
  nodes_selected: [],
  nodes_available: [],


  /*
   * Gets the html select element associated with a given
   * node id for node_id.
   **/
  get_node_element: function(node_id) {
    return $('li > label[for^="id_nodes_' + node_id + '"]');
  },

  /*
   * Initializes an associative array of lists of the current
   * nodes.
   **/
  init_node_list: function () {
    horizon.Node.nodes_selected = [];
    horizon.Node.nodes_available = [];
    $(this.get_node_element("")).each(function () {
      var $this = $(this);
      var $input = $this.children("input");
      var name = horizon.string.escapeHtml($this.text().replace(/^\s+/, ""));
      var node_property = {
        "name": name,
        "id": $input.attr("id"),
        "value": $input.attr("value")
      };
      if ($input.is(":checked")) {
        horizon.Node.nodes_selected.push(node_property);
      } else {
        horizon.Node.nodes_available.push(node_property);
      }
    });
  },

  /*
   * Generates the HTML structure for a node that will be displayed
   * as a list item in the node list.
   **/
  generate_node_element: function(name, id, value) {
    var $li = $('<li>');
    $li.attr('name', value).html(name + '<em class="node_id">(' + value + ')</em><a href="#" class="btn btn-primary"></a>');
    return $li;
  },

  /*
   * Generates the HTML structure for the Node List.
   **/
  generate_nodelist_html: function() {
    var self = this;
    var updateForm = function() {
      var lists = $("#nodeListId li").attr('data-index',100);
      var active_nodes = $("#selected_node > li").map(function(){
        return $(this).attr("name");
      });
      $("#nodeListId .multiple-checkbox input:checkbox").removeAttr('checked');
      active_nodes.each(function(index, value){
        $("#nodeListId input:checkbox[value=" + value + "]")
          .prop('checked', true)
          .parents("li").attr('data-index',index);
      });
      $("#nodeListId ul").html(
        lists.sort(function(a,b){
          if( $(a).data("index") < $(b).data("index")) { return -1; }
          if( $(a).data("index") > $(b).data("index")) { return 1; }
          return 0;
        })
      );
    };
    $("#nodeListSortContainer").show();
    $("#id_nodes").parent().parent().hide();
    self.init_node_list();
    // Make sure we don't duplicate the nodes in the list
    $("#available_node").empty();
    $.each(self.nodes_available, function(index, value){
      $("#available_node").append(self.generate_node_element(value.name, value.id, value.value));
    });
    // Make sure we don't duplicate the nodes in the list
    $("#selected_node").empty();
    $.each(self.nodes_selected, function(index, value){
      $("#selected_node").append(self.generate_node_element(value.name, value.id, value.value));
    });
    $(".nodelist > li > a.btn").click(function(e){
      var $this = $(this);
      e.preventDefault();
      e.stopPropagation();
      if($this.parents("ul#available_node").length > 0) {
        $this.parent().appendTo($("#selected_node"));
      } else if ($this.parents("ul#selected_node").length > 0) {
        $this.parent().appendTo($("#available_node"));
      }
      updateForm();
    });
    if ($("#nodeListId > div.form-group.error").length > 0) {
      var errortext = $("#nodeListId > div.form-group.error").find("span.help-block").text();
      $("#selected_node_label").before($('<div class="dynamic-error">').html(errortext));
    }
    $(".nodelist").sortable({
      connectWith: "ul.nodelist",
      placeholder: "ui-state-highlight",
      distance: 5,
      start:function(e,info){
        $("#selected_node").addClass("dragging");
      },
      stop:function(e,info){
        $("#selected_node").removeClass("dragging");
        updateForm();
      }
    }).disableSelection();
  },

  sc_init: function(modal) {
    // Initialise the drag and drop node list
    horizon.Node.generate_nodelist_html();
  }
};


