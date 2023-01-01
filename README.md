# proxmox-invoice-generator

## How to use it
### Args
This script took multiple arg:

  - client: Name of the client
  - provider_name: Name of the company or person generating the invoice
  - filename: Invoice filename
  - host: IP address or hostname of the Proxmox server
  - user: User of the Proxmox server
  - date: Last month date (we can launch script on 1st to measure last month consumption)
    
### Example

    export PROXMOX_PASSWORD="heavyweather" billings.py --client ME --provider_name YOU --date 202212 --filename invoice.pdf --host 192.168.1.1 --user root@pam
