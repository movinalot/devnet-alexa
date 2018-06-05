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
        faults = handle.query_classid("FaultInst")
    else:
        message = ("was an error connecting to the UCS Manager, " +
            "please check the access credentials or IP address")
        return message
    
    retrieved_vlan = handle.query_dn("fabric/lan/net-vlan" + vlan_id)

    if not retrieved_vlan:
        fabric_lan_cloud = handle.query_dn("fabric/lan")
        vlan = FabricVlan(parent_mo_or_dn=fabric_lan_cloud,
                        name="vlan" + vlan_id,
                        id=vlan_id)

        handle.add_mo(vlan)
        handle.commit()

        retrieved_vlan = handle.query_dn("fabric/lan/net-vlan" + vlan_id)

        if retrieved_vlan and retrieved_vlan.name == "vlan" + vlan_id:
            message = "Vee lan " + vlan_id + " has been added to UCS Manager."
        else:
            message = "Vee lan " + vlan_id + " was not added to UCS Manager."
    else:
        message = "Vee lan " + vlan_id + " alreay exists on UCS Manager."
    
    ucsm_logout()

    return message


def get_ucs_faults():

    ucsm_login()

    if status['login'] == "success":
        faults = handle.query_classid("FaultInst")
    else:
        message = ("there was an error connecting to the UCS Manager, " +
            "please check the access credentials or IP address")
        return message
    
    ucsm_logout()

    sev_critical = 0
    sev_major    = 0
    sev_minor    = 0
    sev_warning  = 0

    for fault in faults:
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

    print get_ucs_faults(), status['login']
    print add_ucs_vlan("100")