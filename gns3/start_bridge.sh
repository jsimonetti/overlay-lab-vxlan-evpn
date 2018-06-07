ubridge -f gns3/ubridge.ini &
sudo ip ad add 192.168.1.1/24 dev tap0
sudo ip link set dev tap0 up
