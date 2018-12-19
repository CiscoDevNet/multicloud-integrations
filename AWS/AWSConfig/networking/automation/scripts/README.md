The script is used to gather the route table IDs and private subnet CIDRs after the CCP automation has created all of the relevant VPC resources.

```
Example use of the script:
./aws-get-vpc-info.sh vpc-043953bf3fd40447c
 The VPC ID BEING USED IS
vpc-043953bf3fd40447c
 GET ROUTE TABLE IDs
 Private route table 1 ID is:
rtb-0b5ed35d499184e53
 Private route table 2 ID is:
rtb-06f537ceb7ec49160
 Private route table 3 ID is:
rtb-02f09cafd1f7db0b5
 GET ALL SUBNET CIDR RANGES
 Private subnet 1 CIDR range is:
172.16.3.0/24
 Private subnet 2 CIDR range is:
172.16.4.0/24
 Private subnet 3 CIDR range is:
172.16.5.0/24
```
