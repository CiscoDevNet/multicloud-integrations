# HX Installer

* Download the HX Installer OVA from the Cisco Software Download website.
    
* Deploying the OVA from the vSphere Client installed previously.
    
* **DNS / DHCP** - The DNS/DHCP host is running on a CentOS 7 VM that will run on the "Shim Hardware" and is provided as an OVA file (`is this valid for AWS`). Deploy this OVA through the vSphere Client.
    
* Change the IP Address and DNS address using the vCenter Console Connection. Recommended values for the fields are:
```shell
    Addresses : 10.xx.1.10/24
    Gateway : 10.x.1.1
    DNS : 127.0.0.1
    Search Domains : eap.cisco.com
```

* Add/Update DHCP Scopes. [Reference Link](https://www.itzgeek.com/how-tos/linux/ubuntu-how-tos/install-and-configure-dhcp-server-on-centos-7-ubuntu-14-04.html)

* Add/Update DNS Entries. [Reference Link](https://www.digitalocean.com/community/tutorials/how-to-configure-bind-as-a-private-network-dns-server-on-centos-7#maintaining-dns-records)
    
* Configure the HX Cluster with the DHCP Relay Policy and DHCP Relay Label. [Reference Link](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/2-x/basic_config/b_APIC_Basic_Config_Guide_2_x/b_APIC_Basic_Config_Guide_2_x_chapter_011.html#concept_231D6CA0A1BB4B27AC730160E003EF29)

* Deploying On­prem CSR1000v on C220 Shim ESX Host
    
    The external guide to deploy CSR1000v can be found [here](https://www.cisco.com/c/en/us/td/docs/routers/csr1000/software/configuration/b_CSR1000v_Configuration_Guide/b_CSR1000v_Configuration_Guide_chapter_011.pdf)