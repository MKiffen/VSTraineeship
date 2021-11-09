#!/bin/bash
cd /vagrant
printf "%b\n" "config=$2"
printf "%b\n Starting provisioner in: "`pwd`
cur_dir="$(dirname "$0")"
source /vagrant/scripts/utils/utils-yaml.sh
source /vagrant/scripts/utils/utils-dns-server.sh
source /vagrant/scripts/utils/utils-dns-client.sh
source /vagrant/scripts/utils/utils-firewall.sh
source /vagrant/scripts/utils/utils-command.sh
source /vagrant/scripts/utils/utils-users.sh
key=$1
cfg=$2
# Get config from yaml
eval $(parse_yaml "${cfg}" "${key}")

eval HOSTNAME=\$$key\_vm_hostname
eval NEWUSER=\$$key\_vm_user
eval BOX=\$$key\_vm_box
eval GUEST_IP=\$$key\_network_ip
eval DOMAIN=\$$key\_network_domain
eval MASTER_DNS_IP=\$$key\_services_dns_nameserver1_ip
eval SLAVE_DNS_IP=\$$key\_services_dns_nameserver2_ip
eval DNS_TYPE=\$$key\_services_dns_type
eval SERVICE_DOCKER_INSTALL=\$$key\_services_docker_install_script
eval SECRETS_FILES=\$$key\_secrets_ssh_key_files

f_in="/opt/vm_config/dns/named.conf" 
f_out="/etc/named.conf" 

sudo hostnamectl set-hostname $HOSTNAME

### SERVICES 
### Install DNS
if [[ $BOX == *"centos"* && ( $DNS_TYPE == "master" || $DNS_TYPE == "slave" ) ]]; then
  install_dns $DNS_TYPE
  configure_firewall
elif [[ ( $BOX == *"ubuntu"* && $DNS_TYPE == "client" ) ]]; then
  install_resolvconf $MASTER_DNS_IP $SLAVE_DNS_IP "local" $DOMAIN
elif [[ ( $BOX == *"centos"* && $DNS_TYPE == "client" ) ]]; then
  nmcli_set_dns $MASTER_DNS_IP $SLAVE_DNS_IP "eth0"
  nmcli_set_dns $MASTER_DNS_IP $SLAVE_DNS_IP "eth1"
fi


install(){
  sudo apt update 

  if [ ! -x "$(command -v xfce-about)" ]; then
    sudo apt install xubuntu-core --quiet -y
  fi

  if [ ! -x "$(command -v x2goversion)" ]; then
    sudo apt-get install x2goserver x2goserver-xsession --quiet -y
    echo "see https://www.digitalocean.com/community/tutorials/how-to-set-up-a-remote-desktop-with-x2go-on-ubuntu-18-04"   
    sudo sed -i 's/BIG-REQUESTS/_IG-REQUESTS/' /usr/lib/x86_64-linux-gnu/libxcb.so.1
    sudo echo "X2GO_NXAGENT_DEFAULT_OPTIONS=\" -extension BIG-REQUESTS\"" >> /etc/x2go/x2goagent.options
    sudo service x2goserver restart
  fi

  if [ ! -x "$(command -v code)" ]; then
    sudo snap install code --classic
  fi

  if [ ! -x "$(command -v dbeaver)" ]; then
    sudo snap install dbeaver-ce
  fi

  if [ ! -x "$(command -v python3-venv)" ]; then
    # Install python virtualenv
    sudo apt-get install python3-venv
    python3 -m venv ~/vm_venv
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.9
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2
  fi
  # install chromium 
  if [ ! -x "$(command -v chromium-browser)" ]; then
    sudo apt install chromium-browser -y
  fi

### Docker
# todo: test for docker-compose
if [[ ! $SERVICE_DOCKER_INSTALL == "" ]]; then
    if [ -x "$(command -v docker)" ]; then
        echo "Update docker"
        # command
    else
        echo "Install docker"
        sh $SERVICE_DOCKER_INSTALL
    fi  
fi

}

remove(){
  sudo apt purge xubuntu-icon-theme xfce4-* -y
  sudo apt autoremove -y
}

install

