#!/bin/bash

export AWS_DEFAULT_OUTPUT="text"

name=$1
VPCID=$1
echo -e "\033[1;31m The VPC ID BEING USED IS \033[0m"
echo -e "\033[1;32m$VPCID\033[0m"

echo -e "\033[1;31m GET ROUTE TABLE IDs \033[0m"

RTBID4=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPCID" "Name=tag:Name,Values=*private-route-table1" --query 'RouteTables[*].[RouteTableId]')
RTBID5=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPCID" "Name=tag:Name,Values=*private-route-table2" --query 'RouteTables[*].[RouteTableId]')
RTBID6=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPCID" "Name=tag:Name,Values=*private-route-table3" --query 'RouteTables[*].[RouteTableId]')


echo -e "\033[1;32m Private route table 1 ID is:\033[0m"
echo $RTBID4
echo -e "\033[1;32m Private route table 2 ID is:\033[0m"
echo $RTBID5
echo -e "\033[1;32m Private route table 3 ID is:\033[0m"
echo $RTBID6

echo -e "\033[1;31m GET ALL SUBNET CIDR RANGES \033[0m"


SUBCIDR4=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values='$VPCID'" "Name=tag:Name,Values=*private-subnet1" --query 'Subnets[*].[CidrBlock]')
SUBCIDR5=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values='$VPCID'" "Name=tag:Name,Values=*private-subnet2" --query 'Subnets[*].[CidrBlock]')
SUBCIDR6=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values='$VPCID'" "Name=tag:Name,Values=*private-subnet3" --query 'Subnets[*].[CidrBlock]')


echo -e "\033[1;32m Private subnet 1 CIDR range is:\033[0m"
echo $SUBCIDR4
echo -e "\033[1;32m Private subnet 2 CIDR range is:\033[0m"
echo $SUBCIDR5
echo -e "\033[1;32m Private subnet 3 CIDR range is:\033[0m"
echo $SUBCIDR6

