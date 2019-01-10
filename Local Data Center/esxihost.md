# Infrastructure ESXi Host

* Configure Disks with RAID 0 capability: Refer the Section `Creating Virtual Drive from Unused Physical Drives` from the [CIMC GUI Configuration Document](https://www.cisco.com/c/en/us/support/servers-unified-computing/ucs-c-series-integrated-management-controller/products-installation-and-configuration-guides-list.html) installed on your host.
  
* Install ESXi 6.0 on the host. You can refer the [Cisco FlexFlash](https://www.cisco.com/c/dam/en/us/solutions/collateral/data-center-virtualization/unified-computing/whitepaper_C11-718938.pdf) whitepaper to install on SD Card or install on the Virtual Disk created above.
  
* Install vCenter 6.0 to manage the HX Cluster. Install the vSphere Client which will allow to deploy the HX Installer OVA.