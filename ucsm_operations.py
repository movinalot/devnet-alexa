def get_ucs_faults():

    from ucsmsdk.ucshandle import UcsHandle

    sev_critical = 0
    sev_major    = 0
    sev_minor    = 0
    sev_warning  = 0

    handle = UcsHandle("128.107.70.141","admin","password")
    handle.login()

    faults = handle.query_classid("FaultInst")
    for fault in faults:
        if fault.severity == 'critical':
            sev_critical += 1
        elif fault.severity == 'major':
            sev_major += 1
        elif fault.severity == 'minor':
            sev_minor += 1
        elif fault.severity == 'warning':
            sev_warning += 1

    handle.logout()

    return str(sev_critical) + "," + str(sev_major) + "," + str(sev_minor)+ "," + str(sev_warning)


if __name__ == "__main__":
    get_ucs_faults()
