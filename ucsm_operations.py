import urllib2
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucssession import UcsException

# Put your UCS Manger IP address here, inside the quotes
#ucsmhost = "Your UCS Manager IP"
ucsmhost = "128.107.70.141"
username = "admin"
password = "password"

handle = None
status = {}

def add_ucs_vlan(vlan_id):

    from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan
    
    ucsm_login()

    if status['login'] == "success":
        response = handle.query_dn("fabric/lan/net-vlan" + vlan_id)
    else:
        message = ("there was an error connecting to the UCS Manager, " +
            "please check the access credentials or IP address")
        return message

    if not response:
        fabric_lan_cloud = handle.query_dn("fabric/lan")
        vlan = FabricVlan(parent_mo_or_dn=fabric_lan_cloud,
                        name="vlan" + vlan_id,
                        id=vlan_id)

        handle.add_mo(vlan)
        handle.commit()

        response = handle.query_dn("fabric/lan/net-vlan" + vlan_id)

        if response and response.name == "vlan" + vlan_id:
            message = "Vee lan " + vlan_id + " has been added to UCS Manager."
        else:
            message = "Vee lan " + vlan_id + " was not added to UCS Manager."
    else:
        message = "Vee lan " + vlan_id + " already exists on UCS Manager."
    
    ucsm_logout()

    return message


def remove_ucs_vlan(vlan_id):
    
    ucsm_login()

    if status['login'] == "success":
        response = handle.query_dn("fabric/lan/net-vlan" + vlan_id)
    else:
        message = ("there was an error connecting to the UCS Manager, " +
            "please check the access credentials or IP address")
        return message

    if response and response.name == "vlan" + vlan_id:
        
        handle.remove_mo(response)
        handle.commit()

        response = handle.query_dn("fabric/lan/net-vlan" + vlan_id)

        if not response:
            message = "Vee lan " + vlan_id + " has been removed from UCS Manager."
        else:
            message = "Vee lan " + vlan_id + " was not removed from UCS Manager."
    else:
        message = "Vee lan " + vlan_id + " does not exist on UCS Manager."
    
    ucsm_logout()

    return message


def get_ucs_faults():

    ucsm_login()

    if status['login'] == "success":
        response = handle.query_classid("FaultInst")
    else:
        message = ("there was an error connecting to the UCS Manager, " +
            "please check the access credentials or IP address")
        return message
    
    ucsm_logout()

    sev_critical = 0
    sev_major    = 0
    sev_minor    = 0
    sev_warning  = 0

    for fault in response:
        if fault.severity == 'critical':
            sev_critical += 1
        elif fault.severity == 'major':
            sev_major += 1
        elif fault.severity == 'minor':
            sev_minor += 1
        elif fault.severity == 'warning':
            sev_warning += 1
 
    message = ("there are " +
        str(sev_critical) + " critical faults, " +
        str(sev_major) + " major faults, " +
        str(sev_minor) + " minor faults, " +
        str(sev_warning) + " warnings")

    return message


def set_ucs_server():

    from ucsmsdk.mometa.macpool.MacpoolBlock import MacpoolBlock
    from ucsmsdk.mometa.ls.LsServer import LsServer
    from ucsmsdk.mometa.ls.LsBinding import LsBinding

    ucsm_login()

    if status['login'] != "success":
        message = ("there was an error connecting to the UCS Manager, " +
            "please check the access credentials or IP address")
        return message
    

    # Add/Update MAC Block
    response = handle.query_dn("org-root/mac-pool-default")
    mo_mac_pool_block = MacpoolBlock(parent_mo_or_dn=response,r_from="00:25:B5:00:00:AA",to="00:25:B5:00:00:D9")
    handle.add_mo(mo_mac_pool_block, modify_present=True)

    # Add/Update Service Profile Template
    mo_sp_template = LsServer(parent_mo_or_dn="org-root", type="initial-template", name="DevNet_Skill_Template")
    handle.add_mo(mo_sp_template, modify_present=True)
    handle.commit()

    # Retrive the MO for the created/updated Service Profile template
    filter_exp = '(name,"DevNet_Skill_Template")'
    mo_sp_templ = handle.query_classid("lsServer",filter_str=filter_exp)
    
    filter_exp = '(name,"DevNet_Skill_*", type="re") and (type,"instance")'
    mo_sp_instances = handle.query_classid("lsServer",filter_str=filter_exp)
    num_sp_instances = len(mo_sp_instances) + 1
    
    if num_sp_instances <= 9:
        service_profile_name = "DevNet_Skill_Server_0" + str(num_sp_instances)
    else:
        service_profile_name = "DevNet_Skill_Server_" + str(num_sp_instances)

    # Find an available compute blade
    response = handle.query_classid("computeBlade")
    for blade in response:
        if blade.admin_state == 'in-service' and blade.association == 'none':
            break

    mo_sp = LsServer(parent_mo_or_dn="org-root", src_templ_name="DevNet_Skill_Template", name=service_profile_name)
    mo_sp_templ_ls_binding = LsBinding(parent_mo_or_dn=mo_sp, pn_dn=blade.dn)
    handle.add_mo(mo_sp, modify_present=True)
    handle.commit()

    ucsm_logout()

    sp_spoken_name = service_profile_name.replace('_',' ')
    message = ("server " + blade.slot_id + " in chassis " + blade.chassis_id + " has been provisioned " +
        "with service profile " + sp_spoken_name)
    return message


def ucsm_login():

    global handle, status

    try:
        handle = UcsHandle(ucsmhost,username,password)
        if handle.login() == True:
            status['login'] = "success"
            return
    
    except urllib2.URLError as err:
        status['login'] = "URLError"
        return

    except UcsException as err:
        status['login'] = "UcsException"
        return

def ucsm_logout():

    handle.logout()


if __name__ == "__main__":

    #print get_ucs_faults(), status['login']
    #print add_ucs_vlan("100")
    #print add_ucs_vlan("110")
    #print add_ucs_vlan("100")

    #print remove_ucs_vlan("100")
    #print remove_ucs_vlan("110")
    #print remove_ucs_vlan("100")

    print set_ucs_server()