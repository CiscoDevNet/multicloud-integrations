#!/bin/sh

set -e

SKIP_STEP=0

usage() {
  echo "usage: $0 [OPTIONS]"
  echo ""
  echo "  OPTIONS:"
  echo "    --stack-prefix=<string>  REQUIRED. Prefix string for stack instances."
  echo "    --on-prem-cidr=<cidr>    REQUIRED. on-prem CIDR for node instances."
  echo "    --skip-to-step=<num>  OPTIONAL.  Start from a setup step number."
  echo "                          Steps:"
  echo "                             1    create VPC, neworks, EKS cluster, etc"
  echo ""
}

function get_stack_status () {
    local stack_nm=$1

    aws cloudformation list-stacks | jq ".StackSummaries[] | select(.StackName==\"$stack_nm\" and .StackStatus!=\"DELETE_COMPLETE\") | .StackStatus"
}

function check_stack_status () {
    local stack_nm=$1

    max_iter=90
    for (( i = 0; i < $max_iter; i++ )); do
        stack_status=$(get_stack_status $stack_nm)
        if [[ "$stack_status" == \"CREATE_COMPLETE\" ]]; then
            echo "Stack \"$stack_nm\" has completed"
            break
        fi
        echo "Waiting on stack create--\"$stack_nm\""
        sleep 10
    done
    if [[ "$stack_status" != \"CREATE_COMPLETE\" ]]; then
        echo "Stack \"$stack_nm\" hasn't finished creating in required time period."
        exit 1
    fi

}

for i in "$@"; do
    case $i in
        -h|--help)
            usage
            exit
            ;;
        --stack-prefix=?*)
            STACKPREFIX=${i#*=}
            ;;
        --key=?*)
            KEY=${i#*=}
            ;;
        --on-prem-cidr=?*)
            ONPREMCIDR=${i#*=}
            ;;
        --skip-to-step=?*)
            SKIP_STEP=${i#*=}
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

if [[ -z "${STACKPREFIX}" || -z "${KEY}" ]]; then
    usage
    exit 1
fi

LOCAL_OS=$(uname)
case $LOCAL_OS in
    Linux)
        echo "Linux"
        SCRIPT=$(readlink -f $0)
        SCRIPTPATH=$(dirname $SCRIPT)
        ;;
    Darwin)
        #echo "OSX"
        curdir=$(pwd)
        SCRIPTPATH=$(cd $(dirname $0); pwd)
        cd $curdir
        ;;
    *)
        echo "Unsupported Local OS type--$LOCAL_OS"
        exit 1
        ;;
esac

#echo "path == $SCRIPTPATH"

TEMPLATE_PATH="${SCRIPTPATH}/../cf"
echo "Template path = \"$TEMPLATE_PATH\""

VpcId=$(aws ec2 describe-vpcs | jq ".Vpcs[] | select(.Tags[]?.Value | contains(\"${STACKPREFIX}\")) | .VpcId")
PublicSubnet=($(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VpcId" "Name=tag:Name,Values=*public-subnet1" | jq '.Subnets[].SubnetId,.Subnets[].CidrBlock' | tr -d '"'))

echo "${PublicSubnet[0]} ${PublicSubnet[1]} "
PrivateSubnet1=($(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VpcId" "Name=tag:Name,Values=*private-subnet1" | jq '.Subnets[].SubnetId,.Subnets[].CidrBlock' | tr -d '"'))
PrivateSubnet2=($(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VpcId" "Name=tag:Name,Values=*private-subnet2" | jq '.Subnets[].SubnetId,.Subnets[].CidrBlock' | tr -d '"'))
PrivateSubnet3=($(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VpcId" "Name=tag:Name,Values=*private-subnet3" | jq '.Subnets[].SubnetId,.Subnets[].CidrBlock' | tr -d '"'))

PublicIntIp1=$(echo ${PublicSubnet[1]} | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+\/[0-9]+/\1.10/')
PrivateIntIp1=$(echo ${PrivateSubnet1[1]} | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+\/[0-9]+/\1.10/')
PrivateGwIp1=$(echo ${PrivateSubnet1[1]} | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+\/[0-9]+/\1.1/')
OspfVpcNetwork=$(echo ${PrivateSubnet1[1]} | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+\/[0-9]+/\1.0/')

if (( ${SKIP_STEP} <= 1 )); then
    PrivateRouteTableId1=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VpcId" "Name=tag:Name,Values=*private-route-table1" | jq '.RouteTables[].RouteTableId' | tr -d '"')
    PrivateRouteTableId2=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VpcId" "Name=tag:Name,Values=*private-route-table2" | jq '.RouteTables[].RouteTableId' | tr -d '"')
    PrivateRouteTableId3=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VpcId" "Name=tag:Name,Values=*private-route-table3" | jq '.RouteTables[].RouteTableId' | tr -d '"')
    
    aws cloudformation create-stack --stack-name ${STACKPREFIX}-csr \
        --template-body file:///${TEMPLATE_PATH}/csr-full-automation-post-ccp-deploy/csr-deploy-post-ccp-vpc-create-clean.yaml \
        --capabilities CAPABILITY_IAM \
        --parameters ParameterKey=VPC,ParameterValue=${VpcId} \
        ParameterKey=Hostname,ParameterValue=multicloud-csr-01 \
        ParameterKey=LicenseModel,ParameterValue=BYOL \
        ParameterKey=KeyName,ParameterValue=${KEY} \
        ParameterKey=InstanceType,ParameterValue=c4.large \
        ParameterKey=InboundSSH,ParameterValue=0.0.0.0/0 \
        ParameterKey=PublicSubnet1,ParameterValue=${PublicSubnet[0]} \
        ParameterKey=PublicInterfaceIP1,ParameterValue=$PublicIntIp1 \
        ParameterKey=PrivateInterfaceIP1,ParameterValue=$PrivateIntIp1 \
        ParameterKey=PrivateSubnet1,ParameterValue=${PrivateSubnet1[0]} \
        ParameterKey=PrivateSubnetCidr1,ParameterValue=${PrivateSubnet1[1]} \
        ParameterKey=PrivateSubnet2,ParameterValue=${PrivateSubnet2[0]} \
        ParameterKey=PrivateSubnetCidr2,ParameterValue=${PrivateSubnet2[1]} \
        ParameterKey=PrivateSubnet3,ParameterValue=${PrivateSubnet3[0]} \
        ParameterKey=PrivateSubnetCidr3,ParameterValue=${PrivateSubnet3[1]} \
        ParameterKey=PrivateGatewayIP1,ParameterValue=$PrivateGwIp1 \
        ParameterKey=PrivateRouteTableId1,ParameterValue=$PrivateRouteTableId1 \
        ParameterKey=PrivateRouteTableId2,ParameterValue=$PrivateRouteTableId2 \
        ParameterKey=PrivateRouteTableId3,ParameterValue=$PrivateRouteTableId3 \
        ParameterKey=OnPremCidr1,ParameterValue=${ONPREMCIDR} \
        ParameterKey=DmvpnIp,ParameterValue=10.250.0.9 \
        ParameterKey=DmvpnNetmask,ParameterValue=255.255.255.0 \
        ParameterKey=OspfVpcNetwork,ParameterValue=$OspfVpcNetwork \
        ParameterKey=OspfVpcWildcard,ParameterValue=0.0.0.255 \
        ParameterKey=OspfTunnelNetwork,ParameterValue=10.250.0.0 \
        ParameterKey=OspfTunnelWildcard,ParameterValue=0.0.0.255 \
        ParameterKey=OspfVpcArea,ParameterValue=2 \
        ParameterKey=OspfTunnelArea,ParameterValue=0 
fi

check_stack_status ${STACKPREFIX}-csr

if (( ${SKIP_STEP} <= 2 )); then
    worker_sg=$(aws ec2 describe-security-groups --filters Name=vpc-id,Values=$VpcId | jq '.SecurityGroups[] | select(.GroupName|test(".*worker.group.*")) | .GroupId' | tr -d '"')
    aws ec2 authorize-security-group-ingress --group-id ${worker_sg} --protocol -1 --cidr 10.0.100.0/24
    aws ec2 authorize-security-group-ingress --group-id ${worker_sg} --protocol -1 --cidr 10.1.0.0/16
fi
