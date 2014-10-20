import horizon

class GroupPolicyPanels(horizon.PanelGroup):
    name = _("Policy")
    slug = "group_policy"
    panels = ('endpoint_groups',
              'network_policy',
			  'application_policy',)
