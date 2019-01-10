# Cisco Hyperflex

The Cisco Hyperflex cluster installation is a standard process, the cluster can be installed by referring to the resources from following links:

* [Pre-requisites](https://www.cisco.com/c/en/us/td/docs/hyperconverged_systems/HyperFlex_HX_DataPlatformSoftware/Installation_VMWare_ESXi/2_5/b_HyperFlexSystems_Installation_Guide_for_VMware_ESXi_2_5/b_HyperFlexSystems_GettingStartedGuide_2_5_chapter_01.html)
    
* [Installing Cisco HyperFlex Systems Servers](https://www.cisco.com/c/en/us/td/docs/hyperconverged_systems/HyperFlex_HX_DataPlatformSoftware/Installation_VMWare_ESXi/2_5/b_HyperFlexSystems_Installation_Guide_for_VMware_ESXi_2_5/b_HyperFlexSystems_GettingStartedGuide_2_5_chapter_010.html)
    
* [Configuring Cisco HyperFlex Systems](https://www.cisco.com/c/en/us/td/docs/hyperconverged_systems/HyperFlex_HX_DataPlatformSoftware/Installation_VMWare_ESXi/2_5/b_HyperFlexSystems_Installation_Guide_for_VMware_ESXi_2_5/b_HyperFlexSystems_GettingStartedGuide_2_5_chapter_011.html)

* Walkthrough of the HX installation system:

    * Deployment of HX Data Platform Installer OVA 
            * Download the required HX Data Platform Installer OVA from [download site](https://software.cisco.com/download/home/286305544/type/286305994/release/3.0%25281e%2529?catid=286305510)
            * Deploy the OVA downloaded above using the vSphere Client.
    
    * Check status of the Servers at UCS Manager before configuring HyperFlex Cluster
            1. Port on the FI that servers are connected to are **UP**
            2. Check the servers are **Unassociated**.
        
    * Configure HyperFlex Clusters by following the instructions from [official installation guide](https://www.cisco.com/c/en/us/td/docs/hyperconverged_systems/HyperFlex_HX_DataPlatformSoftware/Installation_VMWare_ESXi/2_5/b_HyperFlexSystems_Installation_Guide_for_VMware_ESXi_2_5/b_HyperFlexSystems_GettingStartedGuide_2_5_chapter_011.html).
  
  
    * Once the HX Cluster is created, execute the steps mentioned in the [Post Cluster Configuration](https://www.cisco.com/c/en/us/td/docs/hyperconverged_systems/HyperFlex_HX_DataPlatformSoftware/Installation_VMWare_ESXi/2_5/b_HyperFlexSystems_Installation_Guide_for_VMware_ESXi_2_5/b_HyperFlexSystems_GettingStartedGuide_2_5_chapter_0100.html) Document.
    
    * The HyperFlex Cluster 2.5 installation has issues when executing `Run Post-Installation Script` step. The issue has been fixed and to use the fixed _post_install_. When in installer shell execute the following command for the fixed post_install script :
    
    ```shell
        curl ­L http://cs.co/hxupdate | sh
    ```
    
    * When configuring the Data Store for the HX Cluster, a recommended values for the configuration are:
        ```shell
         Datastore Name : HX-Datastore
         Size : 1 TB
         Block Size : 8k
        ```
    
    * Once the datastore is successfully created you will see `HX-Datastore` with `MOUNTED` status